from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from opengever.base.interfaces import IRedirector
from opengever.dossier import _
from opengever.dossier.command import CreateDocumentFromTemplateCommand
from opengever.dossier.templatedossier import get_template_dossier
from opengever.tabbedview.helper import document_with_icon
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.form import Form
from zope import schema
from zope.component import getUtility


class ICreateDocumentFromTemplate(form.Schema):

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True)

    form.widget(recipient=AutocompleteFieldWidget)
    recipient = schema.Choice(
        title=_(u'label_recipient', default=u'Recipient'),
        vocabulary=u'opengever.contact.ContactsVocabulary',
        required=False,
    )

    form.widget(edit_after_creation=SingleCheckBoxFieldWidget)
    edit_after_creation = schema.Bool(
        title=_(u'label_edit_after_creation', default='Edit after creation'),
        default=True,
        required=False,
        )


class TemplateDocumentFormView(AutoExtensibleForm, Form):
    """Show the "Document from template" form.

    This form lists available document templates from template dossiers,
    allows the user to select one and creates a new document by copying the
    template.

    """
    template = ViewPageTemplateFile('templates/document_from_template.pt')

    schema = ICreateDocumentFromTemplate
    ignoreContext = True

    label = _('create_document_with_template',
              default="create document with template")

    has_path_error = False

    @button.buttonAndHandler(_('button_save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        new_doc = self.create_document(data)

        if data.get('edit_after_creation'):
            self.activate_external_editing(new_doc)
            return self.request.RESPONSE.redirect(
                new_doc.absolute_url())

        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '#documents')

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def extractData(self):
        """Also extract path of the selected template from request."""

        data, errors = super(TemplateDocumentFormView, self).extractData()

        paths = self.request.get('paths')
        template_path = paths[0] if paths else None
        if not template_path:
            self.has_path_error = True
            errors = errors + ("template path error",)
        else:
            data['template_path'] = str(template_path)

        return data, errors

    def activate_external_editing(self, new_doc):
        """Check out the given document, and add the external_editor URL
        to redirector queue.
        """

        # Check out the new document
        manager = self.context.restrictedTraverse('checkout_documents')
        manager.checkout(new_doc)

        # Add redirect to the zem-file download,
        # in order to start editing with external editor.
        redirector = IRedirector(self.request)
        redirector.redirect(
            '%s/external_edit' % new_doc.absolute_url(),
            target='_self',
            timeout=1000)

    def create_document(self, data):
        """Create a new document based on a template."""

        template_doc = self.context.restrictedTraverse(data['template_path'])

        command = CreateDocumentFromTemplateCommand(
            self.context, template_doc, data['title'],
            recipient=data.get('recipient'))
        return command.execute()

    def templates(self):
        """List the available template documents the user can choose from.
        """
        template_dossier = get_template_dossier()
        if template_dossier is None:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                _("Not found the templatedossier"), type="error")
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        templatedossier_path = '/'.join(template_dossier.getPhysicalPath())

        catalog = getToolByName(self.context, 'portal_catalog')
        templates = catalog(
            path=dict(
                depth=-1, query=templatedossier_path),
            portal_type="opengever.document.document",
            sort_on='sortable_title',
            sort_order='ascending')

        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')
        columns = (
            ('', helper.path_radiobutton),
            {'column': 'Title',
             'column_title': _(u'label_title', default=u'title'),
             'sort_index': 'sortable_title',
             'transform': document_with_icon},
            {'column': 'Creator',
             'column_title': _(u'label_creator', default=u'Creator'),
             'sort_index': 'document_author'},
            {'column': 'modified',
             'column_title': _(u'label_modified', default=u'Modified'),
             'transform': helper.readable_date}
            )
        return generator.generate(templates, columns)
