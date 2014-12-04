from opengever.base.source import DossierPathSourceBinder
from opengever.core.model import create_session
from opengever.globalindex.oguid import Oguid
from opengever.meeting import _
from opengever.meeting.model.proposal import Proposal as ProposalModel
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from plone.dexterity.content import Container
from plone.directives import form
from z3c.form import interfaces
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.event import notify
from zope.interface import implements
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent


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

    commission = schema.Choice(
        title=_('label_commission', default=u'Commission'),
        source='opengever.meeting.CommissionVocabulary',
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


class Proposal(Container):
    """Act as proxy for the proposal stored in the database.

    """
    implements(IProposal)

    workflow = Workflow([
        State('pending', is_default=True),
        State('submitted'),
        State('scheduled'),
        State('decided'),
        ], [
        Transition('pending', 'submitted',
                   _('submit', default='Submit')),
        Transition('submitted', 'scheduled',
                   _('schedule', default='Schedule')),
        Transition('scheduled', 'decided',
                   _('decide', default='Decide')),
        ])

    @classmethod
    def partition_data(cls, data):
        """Partition input data in model data and plone object data.

        """
        obj_data = {}
        for field_name in IProposal.names():
            if field_name in data:
                obj_data[field_name] = data.pop(field_name)

        return obj_data, data

    def perform_transition(self, name):
        self.workflow.perform_transition(self.load_model(), name)

    def can_perform_transition(self, name):
        return self.workflow.can_perform_transition(self.load_model(), name)

    def get_state(self):
        return self.workflow.get_state(self.load_model().workflow_state)

    def load_model(self):
        oguid = Oguid.for_object(self)
        if oguid is None:
            return None
        return ProposalModel.query.get_by_oguid(oguid)

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
                'label': _('label_commission'),
                'value': model.commission.title,
            },
        ]

    def get_physical_path(self):
        url_tool = self.unrestrictedTraverse('@@plone_tools').url()
        return '/'.join(url_tool.getRelativeContentPath(self))

    def create_model(self, data, context):
        session = create_session()
        oguid = Oguid.for_object(self)
        workflow_state = self.workflow.default_state.name

        aq_wrapped_self = self.__of__(context)
        session.add(ProposalModel(
            oguid=oguid,
            workflow_state=workflow_state,
            physical_path=aq_wrapped_self.get_physical_path(),
            **data))

        # for event handling to work, the object must be acquisition-wrapped
        notify(ObjectModifiedEvent(aq_wrapped_self))

    def update_model(self, data):
        """Store form input in relational database.

        KISS: Currently assumes that each input is a change an thus always
        fires a changed event.

        """
        model = self.load_model()
        for key, value in data.items():
            if value is interfaces.NOT_CHANGED:
                continue
            setattr(model, key, value)

        notify(ObjectModifiedEvent(self))
        return True

    def get_searchable_text(self):
        """Return the searchable text for this proposal.

        This method is called during object-creation, thus the model might not
        yet be created (e.g. when the object is added to its parent).

        """
        model = self.load_model()
        if not model:
            return ''

        return model.get_searchable_text()
