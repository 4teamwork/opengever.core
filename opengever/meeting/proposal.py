from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.source import DossierPathSourceBinder
from opengever.meeting import _
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
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implements
from zope.interface import Interface


class IProposalModel(Interface):
    """Proposal model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        )

    initial_position = schema.Text(
        title=_('label_initial_position', default=u"Initial position"),
        required=False,
        )

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.CommitteeVocabulary',
        required=True)

    proposed_action = schema.Text(
        title=_('label_proposed_action', default=u"Proposed action"),
        description=_("help_proposed_action", default=u""),
        required=False,
    )


class ISubmittedProposalModel(Interface):
    """Submitted proposal model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required=True,
        max_length=256,
        )

    initial_position = schema.Text(
        title=_('label_initial_position', default=u"Initial position"),
        description=_("help_initial_position", default=u""),
        required=False,
        )

    considerations = schema.Text(
        title=_('label_considerations', default=u"Considerations"),
        description=_("help_considerations", default=u""),
        required=False,
        )

    proposed_action = schema.Text(
        title=_('label_proposed_action', default=u"Proposed action"),
        description=_("help_proposed_action", default=u""),
        required=False,
    )


class IProposal(form.Schema):
    """Proposal Proxy Object Schema Interface"""

    relatedItems = RelationList(
        title=_(u'label_documents', default=u'Documents'),
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
        return model.title

    def get_overview_attributes(self):
        model = self.load_model()
        assert model, 'missing db-model for {}'.format(self)

        return [
            {'label': _(u"label_title", default=u'Title'),
             'value': model.title},

            {'label': _('label_initial_position', default=u'Initial position'),
             'value': model.initial_position},

            {'label': _('label_committee', default=u'Committee'),
             'value': model.committee.title},

            {'label': _('label_proposed_action', default=u'Proposed action'),
             'value': model.proposed_action},

            {'label': _('label_workflow_state', default=u'State'),
             'value': self.get_state().title},
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
    workflow = ProposalModel.workflow.with_visible_transitions([])

    def is_editable(self):
        """A proposal in a meeting/committee is editable when not yet decided.

        """
        return self.get_state() in [
            ProposalModel.STATE_SUBMITTED, ProposalModel.STATE_SCHEDULED]

    def get_overview_attributes(self):
        data = super(SubmittedProposal, self).get_overview_attributes()
        model = self.load_model()
        data.extend([
            {
                'label': _('label_considerations', default=u"Considerations"),
                'value': model.considerations,
            },
            {
                'label': _('label_proposal'),
                'value': model.proposed_action,
            },
        ])
        return data

    @classmethod
    def create(cls, proposal, container):
        submitted_proposal = api.content.create(
            type='opengever.meeting.submittedproposal',
            id=cls.generate_submitted_proposal_id(proposal),
            container=container)

        submitted_proposal.sync_model(proposal)
        return submitted_proposal

    @classmethod
    def generate_submitted_proposal_id(cls, proposal):
        return 'submitted-proposal-{}'.format(proposal.proposal_id)

    def get_physical_path(self):
        url_tool = api.portal.get_tool(name="portal_url")
        return '/'.join(url_tool.getRelativeContentPath(self))

    def load_proposal(self, oguid):
        return ProposalModel.query.get_by_oguid(oguid)

    def sync_model(self, proposal_model):
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

        return [document.getObject() for document in documents]

    def is_submit_additional_documents_allowed(self):
        return False


class Proposal(ProposalBase):
    """Act as proxy for the proposal stored in the database.

    """
    content_schema = IProposal
    model_schema = IProposalModel
    model_class = ProposalModel

    implements(content_schema)

    workflow = ProposalModel.workflow.with_visible_transitions(
        ['pending-submitted'])

    def _after_model_created(self, model_instance):
        session = create_session()
        session.add(proposalhistory.Created(proposal=model_instance))

    def is_editable(self):
        """A proposal in a dossier is only editable while not submitted.

        It will remain editable on the submitted side but with a different set
        of editable attributes.

        """
        return self.get_state() == ProposalModel.STATE_PENDING

    def get_documents(self):
        documents = [relation.to_object for relation in self.relatedItems]
        documents.sort(lambda a, b: cmp(b.modified(), a.modified()))
        return documents

    def get_committee(self):
        committee_model = self.load_model().committee
        return committee_model.oguid.resolve_object()

    def get_model_create_arguments(self, context):
        aq_wrapped_self = self.__of__(context)

        workflow_state = self.workflow.default_state.name
        return dict(workflow_state=workflow_state,
                    physical_path=aq_wrapped_self.get_physical_path())

    def get_edit_values(self, fieldnames):
        values = super(Proposal, self).get_edit_values(fieldnames)
        committee = values.pop('committee', None)
        if committee:
            committee = str(committee.committee_id)
            values['committee'] = committee
        return values

    def is_submit_additional_documents_allowed(self):
        return self.get_state() == ProposalModel.STATE_SUBMITTED

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
