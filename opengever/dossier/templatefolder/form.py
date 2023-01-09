from ftw.table import helper
from opengever.base.schema import TableChoice
from opengever.contact import _ as contact_mf
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier import _
from opengever.dossier.command import CreateDocumentFromTemplateCommand
from opengever.kub import is_kub_feature_enabled
from opengever.officeconnector.helpers import is_client_ip_in_office_connector_disallowed_ip_ranges
from opengever.tabbedview.helper import document_with_icon
from plone import api
from plone.autoform import directives as form
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def get_templates(context):
    """We only want to document templates that are directly contained
    in a templatefolder, and not those contained in dossiertemplate
    """
    results = api.content.find(portal_type="opengever.dossier.templatefolder")
    template_folders = [brain.getObject() for brain in results]

    if not template_folders:
        # this may happen when the user does not have permissions to
        # view templates and/or during ++widget++ traversal
        return SimpleVocabulary([])

    templates = []
    for template_folder in template_folders:
        templates.extend(api.content.find(
            context=template_folder,
            depth=1,
            portal_type="opengever.document.document",
            sort_on='sortable_title', sort_order='ascending'))
    templates.sort(key=lambda template: template.Title.lower())

    terms = []
    for brain in templates:
        template = brain.getObject()
        if IDocumentMetadata(template).digitally_available:
            terms.append(SimpleVocabulary.createTerm(
                template,
                str(template.UID()),
                template.title))
    return SimpleVocabulary(terms)


class ICreateDocumentFromTemplate(model.Schema):

    template = TableChoice(
        title=_(u"label_template", default=u"Template"),
        source=get_templates,
        required=True,
        show_filter=True,
        columns=(
            {'column': 'title',
             'column_title': _(u'label_title', default=u'Title'),
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

    form.widget(edit_after_creation=SingleCheckBoxFieldWidget)
    edit_after_creation = schema.Bool(
        title=_(u'label_edit_after_creation', default='Edit after creation'),
        default=True,
        required=False,
    )


class CreateDocumentMixin(object):

    label = _(u'create_document_with_template',
              default=u'Create document from template')

    def finish_document_creation(self, data):
        new_doc = self.create_document(data)

        if data.get('edit_after_creation'):
            self.activate_external_editing(new_doc)
            return self.request.RESPONSE.redirect(
                new_doc.absolute_url())

        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '#documents')

    def activate_external_editing(self, new_doc):
        """Check out the given document, and add the external_editor URL
        to redirector queue.
        """

        # Check out the new document
        manager = self.context.restrictedTraverse('checkout_documents')
        manager.checkout(new_doc)

        new_doc.setup_external_edit_redirect(self.request)

    def create_document(self, data):
        """Create a new document based on a template."""
        command = CreateDocumentFromTemplateCommand(
            self.context, data['template'], data['title'])
        return command.execute()


class SelectTemplateDocumentForm(CreateDocumentMixin, AutoExtensibleForm, Form):

    fields = Fields(ICreateDocumentFromTemplate)
    ignoreContext = True

    def updateFieldsFromSchemata(self):
        super(SelectTemplateDocumentForm, self).updateFieldsFromSchemata()
        if is_client_ip_in_office_connector_disallowed_ip_ranges():
            self.fields = self.fields.omit('edit_after_creation')
        if is_kub_feature_enabled():
            msg = contact_mf(
                u'warning_kub_contact_new_ui_only',
                default=u'Kub contacts are only supported in the new frontend')
            IStatusMessage(self.request).addStatusMessage(msg, type=u'error')

    @property
    def schema(self):
        """Create the schema dynammically and omit recipient if necessary.
        """

        return ICreateDocumentFromTemplate

    @button.buttonAndHandler(_('button_save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        return self.finish_document_creation(data)

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectTemplateDocumentView(FormWrapper):

    form = SelectTemplateDocumentForm
