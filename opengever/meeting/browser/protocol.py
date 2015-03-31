from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base.source import RepositoryPathSourceBinder
from opengever.document.document import IDocumentSchema
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.meeting import _
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import PreProtocolOperations
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.command import ReplaceGeneratedDocumentCommand
from opengever.meeting.command import UpdateGeneratedDocumentCommand
from opengever.meeting.model import GeneratedPreProtocol
from opengever.meeting.model import Meeting
from opengever.repository.repositoryroot import IRepositoryRoot
from plone.directives import form
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import INPUT_MODE
from z3c.relationfield.schema import RelationChoice
from zExceptions import NotFound
from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IChooseDossierSchema(Schema):

    dossier = RelationChoice(
        title=_(u'label_accept_select_dossier',
                default=u'Target dossier'),
        description=_(u'help_accept_select_dossier',
                      default=u'Select the target dossier where the '
                               'pre-protocol should be created.'),
        required=True,

        source=RepositoryPathSourceBinder(
            object_provides='opengever.dossier.behaviors.dossier.IDossierMarker',
            review_state=DOSSIER_STATES_OPEN,
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.'
                    'IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                    ],
                'review_state': ['repositoryroot-state-active',
                                 'repositoryfolder-state-active'] +
                                 DOSSIER_STATES_OPEN,
                }))

    # hidden field
    meeting_id = schema.Int(required=True)


class ChoosePreProtocolDossierForm(Form):
    fields = Fields(IChooseDossierSchema)
    ignoreContext = True
    label = _(u'form_label_generate_preprotocol',
              default=u'Generate pre-protocol')

    operations = PreProtocolOperations

    def updateWidgets(self):
        super(ChoosePreProtocolDossierForm, self).updateWidgets()

        self.widgets['meeting_id'].mode = HIDDEN_MODE
        if not self.widgets['meeting_id'].value:
            initial_value = self.request.get('meeting_id', None)
            self.widgets['meeting_id'].value = initial_value

    @buttonAndHandler(_(u'button_generate', default=u'Generate'), name='save')
    def handle_generate(self, action):
        data, errors = self.extractData()
        if not errors:
            dossier = data['dossier']
            meeting = Meeting.get(data['meeting_id'])

            if not meeting:
                raise NotFound
            # XXX permission checks on meeting?

            command = CreateGeneratedDocumentCommand(
                dossier, meeting, self.operations())
            document = command.execute()
            command.show_message()
            return self.request.RESPONSE.redirect(document.absolute_url())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        data, errors = self.extractData()
        meeting = Meeting.get(data['meeting_id'])
        assert meeting, 'invalid form state, missing meeting'

        return self.request.RESPONSE.redirect(meeting.get_url())


class GeneratePreProtocol(FormWrapper, grok.View):
    grok.context(IRepositoryRoot)
    grok.name('generate_pre_protocol')
    grok.require('zope2.View')

    form = ChoosePreProtocolDossierForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    @classmethod
    def url_for(cls, context, meeting):
        root = context.restrictedTraverse(
            '@@primary_repository_root').get_primary_repository_root()

        return '{}/@@generate_pre_protocol?meeting_id={}'.format(
            root.absolute_url(), meeting.meeting_id)


class ChooseProtocolDossierForm(ChoosePreProtocolDossierForm):

    operations = ProtocolOperations


class GenerateProtocol(GeneratePreProtocol):

    grok.name('generate_protocol')

    form = ChooseProtocolDossierForm

    @classmethod
    def url_for(cls, context, meeting):
        root = context.restrictedTraverse(
            '@@primary_repository_root').get_primary_repository_root()

        return '{}/@@generate_protocol?meeting_id={}'.format(
            root.absolute_url(), meeting.meeting_id)


METHOD_NEW_VERSION = u'new_document_version'
METHOD_NEW_DOCUMENT = u'new_document'


@grok.provider(IContextSourceBinder)
def method_vocabulary_factory(document):
    assert IDocumentSchema.providedBy(document), 'context is not a document'
    dossier = aq_parent(aq_inner(document))
    assert IDossierMarker.providedBy(dossier), ('currently only documents in '
                                                'dossiers are supported')

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
        title=_('label_update_generated_pre_protocol_choose_method',
                default=u'Choose how to update an existing pre-protocol:'),
        source=method_vocabulary_factory,
        required=True)

    # hidden field
    document_id = schema.Int(required=True)


@form.default_value(field=IChooseUpdateMethod['method'])
def default_method(data):
    return METHOD_NEW_VERSION


class ChoosePreProtocolUpdateMethod(Form):
    fields = Fields(IChooseUpdateMethod)
    fields['method'].widgetFactory[INPUT_MODE] = RadioFieldWidget
    ignoreContext = True
    label = _(u'form_label_update_preprotocol',
              default=u'Update pre-protocol')

    operations = PreProtocolOperations

    def updateWidgets(self):
        super(ChoosePreProtocolUpdateMethod, self).updateWidgets()

        self.widgets['document_id'].mode = HIDDEN_MODE
        if not self.widgets['document_id'].value:
            initial_value = self.request.get('document_id', None)
            self.widgets['document_id'].value = initial_value

    @buttonAndHandler(_(u'button_generate', default=u'Generate'), name='save')
    def handle_generate(self, action):
        data, errors = self.extractData()
        if not errors:
            generated_pre_protocol = GeneratedPreProtocol.get(
                data['document_id'])

            if not generated_pre_protocol:
                raise NotFound
            # XXX permission checks on meeting?

            method = data['method']
            if method == METHOD_NEW_DOCUMENT:
                command = ReplaceGeneratedDocumentCommand(
                    generated_pre_protocol, self.operations())
            elif method == METHOD_NEW_VERSION:
                command = UpdateGeneratedDocumentCommand(
                    generated_pre_protocol, self.operations())

            document = command.execute()
            command.show_message()
            return self.request.RESPONSE.redirect(document.absolute_url())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        data, errors = self.extractData()
        meeting = GeneratedPreProtocol.get(data['document_id']).meeting

        assert meeting, 'invalid form state, missing meeting'
        return self.request.RESPONSE.redirect(meeting.get_url())


class UpdatePreProtocol(FormWrapper, grok.View):
    grok.context(IDocumentSchema)
    grok.name('update_pre_protocol')
    grok.require('zope2.View')

    form = ChoosePreProtocolUpdateMethod

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    @classmethod
    def url_for(cls, generated_document):
        document = generated_document.resolve_document()
        return '{}/@@update_pre_protocol?document_id={}'.format(
            document.absolute_url(), generated_document.document_id)


class ChooseProtocolUpdateMethod(ChoosePreProtocolUpdateMethod):

    operations = ProtocolOperations


class UpdateProtocol(UpdatePreProtocol):
    grok.name('update_protocol')

    form = ChooseProtocolUpdateMethod

    @classmethod
    def url_for(cls, generated_document):
        document = generated_document.resolve_document()
        return '{}/@@update_protocol?document_id={}'.format(
            document.absolute_url(), generated_document.document_id)
