from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IReferenceNumber
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.source import DossierPathSourceBinder
from opengever.base.utils import get_preferred_language_code
from opengever.dossier.utils import get_containing_dossier
from opengever.meeting import _
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.command import CopyProposalDocumentCommand
from opengever.meeting.command import CreateSubmittedProposalCommand
from opengever.meeting.command import NullUpdateSubmittedDocumentCommand
from opengever.meeting.command import UpdateSubmittedDocumentCommand
from opengever.meeting.container import ModelContainer
from opengever.meeting.model import proposalhistory
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.model.proposal import Proposal as ProposalModel
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from plone import api
from plone.directives import form
from plone.directives.form import primary
from plone.namedfile.field import NamedBlobFile
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implements
from zope.interface import Interface
from zope.interface import provider
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_title(context):
    return context.title


class IProposalModel(Interface):
    """Proposal model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        defaultFactory=default_title
        )

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.ActiveCommitteeVocabulary',
        required=True)

    legal_basis = schema.Text(
        title=_('label_legal_basis', default=u"Legal basis"),
        required=False,
        )

    initial_position = schema.Text(
        title=_('label_initial_position', default=u"Initial position"),
        required=False,
        )

    proposed_action = schema.Text(
        title=_('label_proposed_action', default=u"Proposed action"),
        required=False,
        )

    decision_draft = schema.Text(
        title=_('label_decision_draft', default=u"Decision draft"),
        required=False,
        )

    publish_in = schema.Text(
        title=_('label_publish_in', default=u"Publish in"),
        required=False,
        )

    disclose_to = schema.Text(
        title=_('label_disclose_to', default=u"Disclose to"),
        required=False,
        )

    copy_for_attention = schema.Text(
        title=_('label_copy_for_attention', default=u"Copy for attention"),
        required=False,
        )

    language = schema.Choice(
        title=_('language', default=u'Language'),
        source='opengever.meeting.LanguagesVocabulary',
        required=True,
        defaultFactory=get_preferred_language_code)


class ISubmittedProposalModel(Interface):
    """Submitted proposal model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        )

    legal_basis = schema.Text(
        title=_('label_legal_basis', default=u"Legal basis"),
        required=False,
        )

    initial_position = schema.Text(
        title=_('label_initial_position', default=u"Initial position"),
        required=False,
        )

    proposed_action = schema.Text(
        title=_('label_proposed_action', default=u"Proposed action"),
        required=False,
        )

    considerations = schema.Text(
        title=_('label_considerations', default=u"Considerations"),
        required=False,
        )

    decision_draft = schema.Text(
        title=_('label_decision_draft', default=u"Decision draft"),
        required=False,
        )

    publish_in = schema.Text(
        title=_('label_publish_in', default=u"Publish in"),
        required=False,
        )

    disclose_to = schema.Text(
        title=_('label_disclose_to', default=u"Disclose to"),
        required=False,
        )

    copy_for_attention = schema.Text(
        title=_('label_copy_for_attention', default=u"Copy for attention"),
        required=False,
        )


class IProposal(form.Schema):
    """Proposal Proxy Object Schema Interface"""

    # The proposal template is only used when creating the proposal.
    # It is easier to keep it as a regular schema field
    # than fiddling the add form.
    proposal_template_path = schema.Choice(
        title=_('label_proposal_template', default=u'Proposal template'),
        source='opengever.meeting.ProposalTemplateVocabulary',
        required=True)

    primary('file')
    file = NamedBlobFile(
        title=_(u'label_proposal_document', default='Proposal document'),
        required=True)

    relatedItems = RelationList(
        title=_(u'label_attachments', default=u'Attachments'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                        ['opengever.dossier.behaviors.dossier.IDossierMarker',
                         'opengever.document.document.IDocumentSchema',
                         'opengever.task.task.ITask',
                         'ftw.mail.mail.IMail', ],
                    }),
            ),
        required=False,
        )


class ISubmittedProposal(IProposal):
    pass


class ProposalBase(ModelContainer):

    workflow = None

    def Title(self):
        model = self.load_model()
        if not model:
            return ''
        return model.title.encode('utf-8')

    def get_overview_attributes(self):
        model = self.load_model()
        assert model, 'missing db-model for {}'.format(self)

        return [
            {'label': _(u"label_title", default=u'Title'),
             'value': model.title},

            {'label': _('label_committee', default=u'Committee'),
             'value': model.committee.get_link(),
             'is_html': True},

            {'label': _('label_meeting', default=u'Meeting'),
             'value': model.get_meeting_link(),
             'is_html': True},

            {'label': _('label_legal_basis', default=u'Legal basis'),
             'value': model.legal_basis,
             'is_html': True},

            {'label': _('label_initial_position', default=u'Initial position'),
             'value': model.initial_position,
             'is_html': True},

            {'label': _('label_proposed_action', default=u'Proposed action'),
             'value': model.proposed_action,
             'is_html': True},

            {'label': _('label_decision_draft', default=u'Decision draft'),
             'value': model.decision_draft,
             'is_html': True},

            {'label': _('label_decision', default=u'Decision'),
             'value': model.get_decision(),
             'is_html': True},

            {'label': _('label_publish_in', default=u'Publish in'),
             'value': model.publish_in,
             'is_html': True},

            {'label': _('label_disclose_to', default=u'Disclose to'),
             'value': model.disclose_to,
             'is_html': True},

            {'label': _('label_copy_for_attention', default=u'Copy for attention'),
             'value': model.copy_for_attention,
             'is_html': True},

            {'label': _('label_workflow_state', default=u'State'),
             'value': self.get_state().title,
             'is_html': True},

            {'label': _('label_decision_number', default=u'Decision number'),
             'value': model.get_decision_number(),
             'is_html': True},
        ]

    def can_execute_transition(self, name):
        return self.workflow.can_execute_transition(self.load_model(), name)

    def execute_transition(self, name):
        self.workflow.execute_transition(self, self.load_model(), name)

    def get_transitions(self):
        return self.workflow.get_transitions(self.get_state())

    def get_state(self):
        return self.load_model().get_state()

    def get_physical_path(self):
        url_tool = api.portal.get_tool(name="portal_url")
        return '/'.join(url_tool.getRelativeContentPath(self))

    def get_searchable_text(self):
        """Return the searchable text for this proposal.

        This method is called during object-creation, thus the model might not
        yet be created (e.g. when the object is added to its parent).

        """
        model = self.load_model()
        if not model:
            return ''

        return model.get_searchable_text()

    def get_committee_admin_unit(self):
        admin_unit_id = self.load_model().committee.admin_unit_id
        return ogds_service().fetch_admin_unit(admin_unit_id)


class SubmittedProposal(ProposalBase):
    """Proxy for a proposal in queue with a committee."""

    content_schema = ISubmittedProposal
    model_schema = ISubmittedProposalModel
    model_class = ProposalModel

    implements(content_schema)
    workflow = ProposalModel.workflow.with_visible_transitions(
        ['submitted-pending'])

    def is_editable(self):
        """A proposal in a meeting/committee is editable when submitted but not
        yet decided.

        """
        return self.load_model().is_editable_in_committee()

    def get_overview_attributes(self):
        data = super(SubmittedProposal, self).get_overview_attributes()
        model = self.load_model()

        # Insert dossier link if dossier exists after committee
        data.insert(
            2, {
                'label': _('label_dossier', default=u"Dossier"),
                'value': self.get_dossier_link(),
                'is_html': True,
            }
        )

        # Insert considerations after proposed_action
        data.insert(
            7, {
                'label': _('label_considerations', default=u"Considerations"),
                'value': model.considerations,
            }
        )

        # Insert discussion after considerations
        agenda = model.agenda_item
        data.insert(
            8, {
                'label': _('label_discussion', default=u"Discussion"),
                'value': agenda and agenda.discussion or ''
            }
        )

        return data

    @classmethod
    def create(cls, proposal, container):
        submitted_proposal = api.content.create(
            type='opengever.meeting.submittedproposal',
            id=cls.generate_submitted_proposal_id(proposal),
            container=container)

        submitted_proposal.sync_model(proposal_model=proposal)
        return submitted_proposal

    @classmethod
    def generate_submitted_proposal_id(cls, proposal):
        return 'submitted-proposal-{}'.format(proposal.proposal_id)

    def get_physical_path(self):
        url_tool = api.portal.get_tool(name="portal_url")
        return '/'.join(url_tool.getRelativeContentPath(self))

    def load_proposal(self, oguid):
        return ProposalModel.query.get_by_oguid(oguid)

    def sync_model(self, proposal_model=None):
        proposal_model = proposal_model or self.load_model()

        proposal_model.submitted_oguid = Oguid.for_object(self)
        proposal_model.submitted_physical_path = self.get_physical_path()
        proposal_model.submitted_admin_unit_id = get_current_admin_unit().id()

    def load_model(self):
        oguid = Oguid.for_object(self)
        if oguid is None:
            return None
        return ProposalModel.query.filter_by(
            submitted_oguid=Oguid.for_object(self)).first()

    def get_documents(self):
        catalog = api.portal.get_tool('portal_catalog')
        documents = catalog(
            portal_type=['opengever.document.document', 'ftw.mail.mail'],
            path=dict(query='/'.join(self.getPhysicalPath())),
            sort_on='modified',
            sort_order='reverse')

        excerpt = self.get_excerpt()
        all_docs = [document.getObject() for document in documents]
        return [doc for doc in all_docs if doc != excerpt]

    def get_excerpt(self):
        return self.load_model().resolve_submitted_excerpt_document()

    def is_submit_additional_documents_allowed(self):
        return False

    def reject(self, text):
        proposal = self.load_model()
        proposal.reject(text)

        with elevated_privileges():
            api.content.delete(self)

    def get_containing_dossier(self):
        model = self.load_model()
        proposal = model.resolve_proposal()
        if not proposal:
            return None
        return get_containing_dossier(proposal)

    def get_dossier_link(self):
        dossier = self.get_containing_dossier()
        if not dossier:
            return _('label_dossier_not_available',
                     default=u"Dossier not available")

        return u'<a href="{0}" title="{1}">{1}</a>'.format(
            dossier.absolute_url(),
            dossier.title)


class Proposal(ProposalBase):
    """Act as proxy for the proposal stored in the database.

    """
    content_schema = IProposal
    model_schema = IProposalModel
    model_class = ProposalModel

    implements(content_schema)

    workflow = ProposalModel.workflow.with_visible_transitions(
        ['pending-submitted', 'pending-cancelled', 'cancelled-pending'])

    def _after_model_created(self, model_instance):
        session = create_session()
        session.add(proposalhistory.Created(proposal=model_instance))

    def is_editable(self):
        """A proposal in a dossier is only editable while not submitted.

        It will remain editable on the submitted side but with a different set
        of editable attributes.

        """
        return self.load_model().is_editable_in_dossier()

    def get_documents(self):
        documents = [relation.to_object for relation in self.relatedItems]
        documents.sort(lambda a, b: cmp(b.modified(), a.modified()))
        return documents

    def get_excerpt(self):
        return self.load_model().resolve_excerpt_document()

    def get_committee(self):
        committee_model = self.load_model().committee
        return committee_model.oguid.resolve_object()

    def get_containing_dossier(self):
        return get_containing_dossier(self)

    def get_repository_folder_title(self, language):
        main_dossier = self.get_containing_dossier().get_main_dossier()
        repository_folder = aq_parent(aq_inner(main_dossier))
        return repository_folder.Title(language=language,
                                       prefix_with_reference_number=False)

    def update_model_create_arguments(self, data, context):
        aq_wrapped_self = self.__of__(context)

        workflow_state = self.workflow.default_state.name
        reference_number = IReferenceNumber(
            context.get_main_dossier()).get_number()

        language = data.get('language')
        repository_folder_title = aq_wrapped_self.get_repository_folder_title(
            language)

        data.update(dict(workflow_state=workflow_state,
                         physical_path=aq_wrapped_self.get_physical_path(),
                         dossier_reference_number=reference_number,
                         repository_folder_title=repository_folder_title,
                         creator=aq_wrapped_self.Creator()))
        return data

    def update_model(self, data):
        language = data.get('language')
        data['repository_folder_title'] = self.get_repository_folder_title(
            language)
        return super(Proposal, self).update_model(data)

    def get_edit_values(self, fieldnames):
        values = super(Proposal, self).get_edit_values(fieldnames)
        committee = values.pop('committee', None)
        if committee:
            committee = str(committee.committee_id)
            values['committee'] = committee
        return values

    def sync_model(self, proposal_model=None):
        proposal_model = proposal_model or self.load_model()

        reference_number = IReferenceNumber(
            self.get_containing_dossier().get_main_dossier()).get_number()
        repository_folder_title = self.get_repository_folder_title(
            proposal_model.language)

        proposal_model.physical_path = self.get_physical_path()
        proposal_model.dossier_reference_number = reference_number
        proposal_model.repository_folder_title = repository_folder_title

    def is_submit_additional_documents_allowed(self):
        return self.load_model().is_submit_additional_documents_allowed()

    def submit_additional_document(self, document):
        assert self.is_submit_additional_documents_allowed()

        submitted_document = SubmittedDocument.query.get_by_source(
            self, document)
        proposal_model = self.load_model()

        if submitted_document:
            if submitted_document.is_up_to_date(document):
                command = NullUpdateSubmittedDocumentCommand(document)
            else:
                command = UpdateSubmittedDocumentCommand(
                    self, document, submitted_document)

        else:
            command = CopyProposalDocumentCommand(
                self,
                document,
                target_path=proposal_model.submitted_physical_path,
                target_admin_unit_id=proposal_model.submitted_admin_unit_id)

            if not self.relatedItems:
                # The missing_value attribute of a z3c-form field is used
                # as soon as an object has no default_value i.e. after creating
                # an object trough the command-line.
                #
                # Because the relatedItems field needs a list as a missing_value,
                # we will fall into the "mutable keyword argument"-python gotcha.
                # The relatedItems will be shared between the object-instances.
                #
                # Unfortunately the z3c-form field does not provide a
                # missing_value-factory (like the defaultFactory) which would be
                # necessary to fix this issue properly.
                #
                # As a workaround we reassign the field with a new list if the
                # relatedItems-attribute has never been assigned before.
                self.relatedItems = []

            self.relatedItems.append(
                RelationValue(getUtility(IIntIds).getId(document)))

        command.execute()
        return command

    def submit(self):
        documents = self.get_documents()
        create_command = CreateSubmittedProposalCommand(self)
        copy_commands = [
            CopyProposalDocumentCommand(
                self, document, parent_action=create_command)
            for document in documents]

        create_command.execute()
        for copy_command in copy_commands:
            copy_command.execute()

    def copy_proposal_template_file_to_proposal(self):
        """This method is called when adding a new proposal.
        It copies the file of the proposal template into our "file"
        blob field for futher editing.
        """
        if not is_word_meeting_implementation_enabled():
            raise ValueError('Unexpected call while the word meeting'
                             ' feature is disabled.')

        if not getattr(self, 'proposal_template_path', None):
            raise ValueError(
                'Missing proposal_template_path value for {!r}'.format(self))

        proposal_template = getSite().restrictedTraverse(
            self.proposal_template_path)

        # This loads the binary data into memory, which is obviously bad.
        # I couldn't find a better way to clone the blob though.
        self.file = IProposal['file']._type(
            data=proposal_template.file.open().read(),
            contentType=proposal_template.file.contentType,
            filename=proposal_template.file.filename)
