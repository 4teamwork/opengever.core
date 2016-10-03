from five import grok
from ftw.table import helper
from opengever.base.interfaces import IRedirector
from opengever.base.schema import TableChoice
from opengever.dossier import _
from opengever.dossier.command import CreateDocumentFromTemplateCommand
from opengever.dossier.templatedossier import get_template_dossier
from opengever.tabbedview.helper import document_with_icon
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.form import Form
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


@grok.provider(IContextSourceBinder)
def get_templates(context):
    template_dossier = get_template_dossier()
    templatedossier_path = '/'.join(template_dossier.getPhysicalPath())

    catalog = api.portal.get_tool('portal_catalog')
    templates = catalog(
        path=dict(
            depth=-1, query=templatedossier_path),
        portal_type="opengever.document.document",
        sort_on='sortable_title',
        sort_order='ascending')

    intids = getUtility(IIntIds)

    terms = []
    for brain in templates:
        template = brain.getObject()
        terms.append(SimpleVocabulary.createTerm(
            template,
            str(intids.getId(template)),
            template.title))
    return SimpleVocabulary(terms)


class ICreateDocumentFromTemplate(form.Schema):

    template = TableChoice(
        title=_(u"label_template", default=u"Template"),
        source=get_templates,
        required=True,
        columns=(
            {'column': 'title',
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
    )

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

    ignoreContext = True
    schema = ICreateDocumentFromTemplate

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

        command = CreateDocumentFromTemplateCommand(
            self.context, data['template'], data['title'],
            recipient=data.get('recipient'))
        return command.execute()
