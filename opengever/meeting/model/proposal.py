from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.meeting import _
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import proposalhistory
from opengever.meeting.model.query import ProposalQuery
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.base.utils import ogds_service
from plone import api
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Submit(Transition):

    def execute(self, obj, model):
        super(Submit, self).execute(obj, model)
        assert obj, 'submitting requires a plone context object.'
        obj.submit()


class Proposal(Base):
    """Sql representation of a proposal."""

    query_cls = ProposalQuery

    __tablename__ = 'proposals'
    __table_args__ = (
        UniqueConstraint('admin_unit_id', 'int_id'),
        UniqueConstraint('submitted_admin_unit_id', 'submitted_int_id'),
        {})

    proposal_id = Column("id", Integer, Sequence("proposal_id_seq"),
                         primary_key=True)
    admin_unit_id = Column(String(30), nullable=False)
    int_id = Column(Integer, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    physical_path = Column(String(256), nullable=False)

    submitted_admin_unit_id = Column(String(30))
    submitted_int_id = Column(Integer)
    submitted_oguid = composite(
        Oguid, submitted_admin_unit_id, submitted_int_id)
    submitted_physical_path = Column(String(256))

    title = Column(String(256), nullable=False)
    workflow_state = Column(String(256), nullable=False)
    initial_position = Column(Text)
    proposed_action = Column(Text)

    considerations = Column(Text)

    committee_id = Column(Integer, ForeignKey('committees.id'))
    committee = relationship('Committee', backref='proposals')

    history_records = relationship('ProposalHistory',
                                   order_by="desc(ProposalHistory.created)")

    # workflow definition
    STATE_PENDING = State('pending', is_default=True,
                          title=_('pending', default='Pending'))
    STATE_SUBMITTED = State('submitted',
                            title=_('submitted', default='Submitted'))
    STATE_SCHEDULED = State('scheduled',
                            title=_('scheduled', default='Scheduled'))
    STATE_DECIDED = State('decided', title=_('decided', default='Decided'))

    workflow = Workflow([
        STATE_PENDING,
        STATE_SUBMITTED,
        STATE_SCHEDULED,
        STATE_DECIDED
        ], [
        Submit('pending', 'submitted',
               title=_('submit', default='Submit')),
        Transition('submitted', 'scheduled',
                   title=_('schedule', default='Schedule')),
        Transition('scheduled', 'submitted',
                   title=_('un-schedule', default='Remove from schedule')),
        Transition('scheduled', 'decided',
                   title=_('decide', default='Decide')),
        ])

    def __repr__(self):
        return "<Proposal {}@{}>".format(self.int_id, self.admin_unit_id)

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

    def execute_transition(self, name):
        self.workflow.execute_transition(None, self, name)

    def get_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.admin_unit_id)

    def get_submitted_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.submitted_admin_unit_id)

    @property
    def id(self):
        return self.proposal_id

    def get_searchable_text(self):
        searchable = filter(None, [self.title, self.initial_position])
        return ' '.join([term.encode('utf-8') for term in searchable])

    def get_link(self):
        return self._get_link(self.get_admin_unit(), self.physical_path)

    def get_submitted_link(self):
        return self._get_link(self.get_submitted_admin_unit(),
                              self.submitted_physical_path)

    def _get_link(self, admin_unit, physical_path):
        if not (admin_unit and physical_path):
            return ''
        url = '/'.join((admin_unit.public_url, physical_path))
        link = u'<a href="{0}" title="{1}">{1}</a>'.format(url, self.title)

        transformer = api.portal.get_tool('portal_transforms')
        return transformer.convertTo('text/x-html-safe', link).getData()

    def getPath(self):
        """This method is required by a tabbedview."""

        return self.physical_path

    def can_be_scheduled(self):
        return self.get_state() == self.STATE_SUBMITTED

    def schedule(self, meeting):
        assert self.can_be_scheduled()

        self.execute_transition('submitted-scheduled')
        session = create_session()
        session.add(AgendaItem(meeting=meeting, proposal=self))
        session.add(proposalhistory.Scheduled(proposal=self))

    def remove_scheduled(self, meeting):
        self.execute_transition('scheduled-submitted')
        session = create_session()
        session.add(proposalhistory.RemoveScheduled(proposal=self))
