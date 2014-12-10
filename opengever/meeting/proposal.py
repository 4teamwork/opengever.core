from opengever.base.source import DossierPathSourceBinder
from opengever.meeting import _
from opengever.meeting.container import ModelContainer
from opengever.meeting.model.proposal import Proposal as ProposalModel
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
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
        description=_('help_title', default=u""),
        required=True,
        max_length=256,
        )

    initial_position = schema.Text(
        title=_('label_initial_position', default=u"Proposal"),
        description=_("help_initial_position", default=u""),
        required=False,
        )

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.CommitteeVocabulary',
        required=True)


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


class Submit(Transition):

    def execute(self, obj, model):
        super(Submit, self).execute(obj, model)
        documents = obj.get_documents()
        create_action = CreateRemoteProposal(obj)
        copy_actions = [ProposalDocumentCopy(document, create_action)
                        for document in documents]

        create_action.execute()
        for copy_action in copy_actions:
            copy_action.execute()


class CreateRemoteProposal(object):

    def __init__(self, proposal):
        self.proposal = proposal
        self.committee_proposal = None

    def execute(self):
        self.committee_proposal = api.content.create(
            type='opengever.meeting.submittedproposal',
            id=self.proposal.get_queued_proposal_id(),
            container=self.proposal.get_committee())


class ProposalDocumentCopy(object):

    def __init__(self, document, parent_action):
        self.document = document
        self.parent_action = parent_action

    def execute(self):
        assert self.parent_action.committee_proposal
        destination = self.parent_action.committee_proposal
        OgCopy(self.document, destination).run()


class OgCopy(object):

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def run(self):
        api.content.copy(self.source, self.destination)


class QueuedProposal(ModelContainer):
    """Proxy for a proposal in queue with a commission."""

    content_schema = IProposal
    model_schema = IProposalModel
    model_class = ProposalModel

    implements(content_schema)


class Proposal(ModelContainer):
    """Act as proxy for the proposal stored in the database.

    """
    content_schema = IProposal
    model_schema = IProposalModel
    model_class = ProposalModel

    implements(content_schema)

    workflow = Workflow([
        State('pending', is_default=True,
              title=_('pending', default='Pending')),
        State('submitted', title=_('submitted', default='Submited')),
        State('scheduled', title=_('scheduled', default='Scheduled')),
        State('decided', title=_('decided', default='Decided')),
        ], [
        Submit('pending', 'submitted',
               title=_('submit', default='Submit')),
        Transition('submitted', 'scheduled',
                   title=_('schedule', default='Schedule')),
        Transition('scheduled', 'decided',
                   title=_('decide', default='Decide')),
        ])

    def get_queued_proposal_id(self):
        model = self.load_model()
        return 'submitted-proposal-{}'.format(model.proposal_id)

    def get_documents(self):
        return [relation.to_object for relation in self.relatedItems]

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

    def execute_transition(self, name):
        self.workflow.execute_transition(self, self.load_model(), name)

    def can_execute_transition(self, name):
        return self.workflow.can_execute_transition(self.load_model(), name)

    def get_state(self):
        return self.workflow.get_state(self.load_model().workflow_state)

    def get_overview_attributes(self):
        model = self.load_model()
        assert model, 'missing db-model for {}'.format(self)

        return [
            {
                'label': _('label_title'),
                'value': model.title,
            },
            {
                'label': _('label_initial_position'),
                'value': model.initial_position,
            },
            {
                'label': _('label_committee'),
                'value': model.committee.title,
            },
            {
                'label': _('label_workflow_state'),
                'value': self.get_state().title,
            },

        ]

    def get_physical_path(self):
        url_tool = self.unrestrictedTraverse('@@plone_tools').url()
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
