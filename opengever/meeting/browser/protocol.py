from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.document.document import IDocumentSchema
from opengever.meeting import _
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.command import ReplaceGeneratedDocumentCommand
from opengever.meeting.command import UpdateGeneratedDocumentCommand
from opengever.meeting.interfaces import IMeetingDossier
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import Meeting
from plone.directives import form
from plone.directives.form import Schema
from plone.protect.utils import addTokenToUrl
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import INPUT_MODE
from zExceptions import NotFound
from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class GenerateProtocol(grok.View):
    grok.context(IMeetingDossier)
    grok.name('generate_protocol')
    grok.require('cmf.AddPortalContent')

    operations = ProtocolOperations()

    @classmethod
    def url_for(cls, meeting):
        dossier = meeting.get_dossier()
        url = '{}/@@generate_protocol?meeting-id={}'.format(
            dossier.absolute_url(), meeting.meeting_id)
        return addTokenToUrl(url)

    def get_meeting(self):
        meeting_id = self.request.get('meeting-id')
        if not meeting_id:
            raise NotFound

        meeting = Meeting.get(meeting_id)
        if not meeting:
            raise NotFound

        return meeting

    def render(self):
        meeting = self.get_meeting()

        command = CreateGeneratedDocumentCommand(
            self.context, meeting, self.operations,
            lock_document_after_creation=True)
        command.execute()
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())


METHOD_NEW_VERSION = u'new_document_version'
METHOD_NEW_DOCUMENT = u'new_document'


@grok.provider(IContextSourceBinder)
def method_vocabulary_factory(document):
    assert IDocumentSchema.providedBy(document), 'context is not a document'
    dossier = aq_parent(aq_inner(document))
    assert IMeetingDossier.providedBy(dossier), (
        'currently only documents in meeting-dossiers are supported')

    return SimpleVocabulary([
        SimpleTerm(
            value=METHOD_NEW_VERSION,
            title=_(u'new_document_version',
                    default=u'Create a new document version for document ${title}',
                    mapping={'title': document.title})),

        SimpleTerm(
            value=METHOD_NEW_DOCUMENT,
            title=_(u'new_document',
                    default=u'Create a new document in dossier ${title}',
                    mapping={'title': dossier.title})),
        ])


class IChooseUpdateMethod(Schema):

    method = schema.Choice(
        title=_('label_update_generated_protocol_choose_method',
                default=u'Choose how to update an existing protocol:'),
        source=method_vocabulary_factory,
        required=True)

    # hidden field
    document_id = schema.Int(required=True)


@form.default_value(field=IChooseUpdateMethod['method'])
def default_method(data):
    return METHOD_NEW_VERSION


class ChooseProtocolUpdateMethod(Form):
    fields = Fields(IChooseUpdateMethod)
    fields['method'].widgetFactory[INPUT_MODE] = RadioFieldWidget
    ignoreContext = True
    label = _(u'form_label_update_protocol',
              default=u'Update protocol')

    operations = ProtocolOperations()

    def updateWidgets(self):
        super(ChooseProtocolUpdateMethod, self).updateWidgets()

        self.widgets['document_id'].mode = HIDDEN_MODE
        if not self.widgets['document_id'].value:
            initial_value = self.request.get('document_id', None)
            self.widgets['document_id'].value = initial_value

    @buttonAndHandler(_(u'button_generate', default=u'Generate'), name='save')
    def handle_generate(self, action):
        data, errors = self.extractData()
        if not errors:
            generated_document = self.get_generated_document(
                data['document_id'])

            if not generated_document:
                raise NotFound
            # XXX permission checks on meeting?

            method = data['method']
            if method == METHOD_NEW_DOCUMENT:
                command = ReplaceGeneratedDocumentCommand(
                    generated_document, self.operations)
            elif method == METHOD_NEW_VERSION:
                command = UpdateGeneratedDocumentCommand(
                    generated_document, self.operations)

            document = command.execute()
            command.show_message()
            return self.request.RESPONSE.redirect(document.absolute_url())

    def get_generated_document(self, document_id):
        return GeneratedProtocol.get(document_id)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        data, errors = self.extractData()
        meeting = GeneratedProtocol.get(data['document_id']).meeting

        assert meeting, 'invalid form state, missing meeting'
        return self.request.RESPONSE.redirect(meeting.get_url())


class UpdateProtocol(FormWrapper, grok.View):
    grok.context(IDocumentSchema)
    grok.name('update_protocol')
    grok.require('cmf.ModifyPortalContent')

    form = ChooseProtocolUpdateMethod

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    @classmethod
    def url_for(cls, generated_document):
        document = generated_document.resolve_document()
        return '{}/@@update_protocol?document_id={}'.format(
            document.absolute_url(), generated_document.document_id)
