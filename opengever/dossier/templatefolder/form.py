from five import grok
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.table import helper
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.interfaces import IRedirector
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.schema import TableChoice
from opengever.contact import is_contact_feature_enabled
from opengever.contact.sources import ContactsSourceBinder
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier import _
from opengever.dossier.command import CreateDocumentFromTemplateCommand
from opengever.dossier.templatefolder import get_template_folder
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.tabbedview.helper import document_with_icon
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from plone.z3cform.layout import FormWrapper
from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
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
    template_folder = get_template_folder()

    if template_folder is None:
        # this may happen when the user does not have permissions to
        # view templates and/or during ++widget++ traversal
        return SimpleVocabulary([])

    templates = api.content.find(
        context=template_folder,
        depth=-1,
        portal_type="opengever.document.document",
        sort_on='sortable_title', sort_order='ascending')

    intids = getUtility(IIntIds)
    terms = []
    for brain in templates:
        template = brain.getObject()
        if IDocumentMetadata(template).digitally_available:
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

    form.widget('recipient', KeywordFieldWidget, async=True)
    recipient = schema.Choice(
        title=_(u'label_recipient', default=u'Recipient'),
        source=ContactsSourceBinder(),
        required=False,
    )

    form.widget(edit_after_creation=SingleCheckBoxFieldWidget)
    edit_after_creation = schema.Bool(
        title=_(u'label_edit_after_creation', default='Edit after creation'),
        default=True,
        required=False,
        )


def get_dm_key(context):
    """Return the key used to store template-data in the wizard-storage."""

    container_oguid = Oguid.for_object(context)
    return 'add_document_from_template:{}'.format(container_oguid)


class CreateDocumentMixin(object):

    label = _(u'create_document_with_template',
              default=u'Create document from template')

    @property
    def steps(self):
        if not is_contact_feature_enabled():
            return []
        return [('select-document', _(u'Select document')),
                ('select-address', _(u'Select recipient address'))]

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

        # Add redirect to the zem-file download,
        # in order to start editing with external editor.
        redirector = IRedirector(self.request)

        if not is_officeconnector_checkout_feature_enabled():
            redirector.redirect(
                '%s/external_edit' % new_doc.absolute_url(),
                target='_self',
                timeout=1000)
        else:
            redirector.redirect(create_oc_url(
                self.request,
                new_doc,
                dict(action='checkout'),
            ))

    def create_document(self, data):
        """Create a new document based on a template."""

        recipient_data = filter(None, [
            data.get('recipient'),
            data.get('address'),
            data.get('mail_address'),
            data.get('phonenumber'),
            data.get('url'),
        ])

        command = CreateDocumentFromTemplateCommand(
            self.context, data['template'], data['title'],
            recipient_data=recipient_data)
        return command.execute()


class SelectTemplateDocumentWizardStep(
        CreateDocumentMixin, AutoExtensibleForm, BaseWizardStepForm, Form):

    step_name = 'select-document'

    def updateFieldsFromSchemata(self):
        super(SelectTemplateDocumentWizardStep, self).updateFieldsFromSchemata()
        if not is_contact_feature_enabled():
            self.fields = self.fields.omit('recipient')

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

        if data.get('recipient'):
            dm = getUtility(IWizardDataStorage)
            dm.update(get_dm_key(self.context), data)
            return self.request.RESPONSE.redirect(
                "{}/select-address".format(self.context.absolute_url()))

        return self.finish_document_creation(data)

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectTemplateDocumentView(FormWrapper):

    form = SelectTemplateDocumentWizardStep


def get_recipient(context):
    """Return the previously selected recipient.

    If it is an unpickled/detached mapper merge it into the current session,
    this triggers a reload of the mapped instance.
    """

    dm = getUtility(IWizardDataStorage)
    data = dm.get_data(get_dm_key(context))

    recipient = data['recipient']
    try:
        # merge unpickled recipient into session when it is a mapper
        if inspect(recipient).detached:
            recipient = create_session().merge(recipient)
    except NoInspectionAvailable:
        pass
    return recipient


@grok.provider(IContextSourceBinder)
def make_address_vocabulary(context):
    recipient = get_recipient(context)

    return SimpleVocabulary([
        SimpleVocabulary.createTerm(
            address, str(address.address_id))
        for address in recipient.addresses])


def address_lines(item, value):
    return u"<br />".join(item.get_lines())


@grok.provider(IContextSourceBinder)
def make_mail_address_vocabulary(context):
    recipient = get_recipient(context)

    return SimpleVocabulary([
        SimpleVocabulary.createTerm(
            mail_address, str(mail_address.mailaddress_id))
        for mail_address in recipient.mail_addresses])


@grok.provider(IContextSourceBinder)
def make_phonenumber_vocabulary(context):
    recipient = get_recipient(context)

    return SimpleVocabulary([
        SimpleVocabulary.createTerm(
            phone_number, str(phone_number.phone_number_id))
        for phone_number in recipient.phonenumbers])


@grok.provider(IContextSourceBinder)
def make_url_vocabulary(context):
    recipient = get_recipient(context)

    return SimpleVocabulary([
        SimpleVocabulary.createTerm(
            url, str(url.url_id))
        for url in recipient.urls])


class ISelectRecipientAddress(form.Schema):

    address = TableChoice(
        title=_(u"label_address", default=u"Address"),
        required=False,
        source=make_address_vocabulary,
        columns=(
            {'column': 'label',
             'column_title': _(u'label_label', default=u'Label')},
            {'column': 'address',
             'column_title': _(u'label_address', default=u'Address'),
             'transform': address_lines},
        ))

    mail_address = TableChoice(
        title=_(u"label_mail_address", default=u"Mail-Address"),
        required=False,
        source=make_mail_address_vocabulary,
        columns=(
            {'column': 'label',
             'column_title': _(u'label_label', default=u'Label')},
            {'column': 'address',
             'column_title': _(u'label_mail_address', default=u'Mail-Address')},
        ))

    phonenumber = TableChoice(
        title=_(u"label_phonenumber", default=u"Phonenumber"),
        required=False,
        source=make_phonenumber_vocabulary,
        columns=(
            {'column': 'label',
             'column_title': _(u'label_label', default=u'Label')},
            {'column': 'phone_number',
             'column_title': _(u'label_phonenumber', default=u'Phonenumber')},
        ))

    url = TableChoice(
        title=_(u"label_url", default=u"URL"),
        required=False,
        source=make_url_vocabulary,
        columns=(
            {'column': 'label',
             'column_title': _(u'label_label', default=u'Label')},
            {'column': 'url',
             'column_title': _(u'label_url', default=u'URL')},
        ))


class SelectAddressWizardStep(
        CreateDocumentMixin, AutoExtensibleForm, BaseWizardStepForm, Form):

    step_name = 'select-address'
    schema = ISelectRecipientAddress

    @button.buttonAndHandler(_('button_save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        dm = getUtility(IWizardDataStorage)
        data.update(dm.get_data(get_dm_key(self.context)))

        return self.finish_document_creation(data)

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectAddressView(FormWrapper):

    form = SelectAddressWizardStep
