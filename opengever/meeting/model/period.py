from opengever.base.model import Base
from opengever.base.model import SQLFormSupport
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from plone import api
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Period(Base, SQLFormSupport):

    STATE_ACTIVE = State('active', is_default=True,
                         title=_('active', default='Active'))
    STATE_CLOSED = State('closed', title=_('closed', default='Closed'))

    workflow = Workflow([
        STATE_ACTIVE,
        STATE_CLOSED,
        ], [
        Transition('active', 'closed',
                   title=_('close_period', default='Close period')),
        ])

    __tablename__ = 'periods'

    period_id = Column('id', Integer, Sequence('periods_id_seq'),
                       primary_key=True)
    committee_id = Column('committee_id', Integer, ForeignKey('committees.id'),
                          nullable=False)
    committee = relationship('Committee', backref='periods')
    workflow_state = Column(String(WORKFLOW_STATE_LENGTH), nullable=False,
                            default=workflow.default_state.name)
    title = Column(String(256), nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    decision_sequence_number = Column(Integer, nullable=False, default=0)
    meeting_sequence_number = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return '<Period {}>'.format(repr(self.title))

    @property
    def wrapper_id(self):
        return 'period-{}'.format(self.period_id)

    def is_removable(self):
        return False

    def get_title(self):
        return u'{} ({} - {})'.format(
            self.title, self.get_date_from(), self.get_date_to())

    def get_url(self, context, view=None):
        elements = [context.absolute_url(), self.wrapper_id]
        if view:
            elements.append(view)

        return '/'.join(elements)

    def get_date_from(self):
        """Return a localized date."""

        return api.portal.get_localized_time(datetime=self.date_from)

    def get_date_to(self):
        """Return a localized date."""

        return api.portal.get_localized_time(datetime=self.date_to)

    def execute_transition(self, name):
        self.workflow.execute_transition(self, self, name)

    def can_execute_transition(self, name):
        return self.workflow.can_execute_transition(self, name)

    def get_toc_template(self):
        return self.committee.get_toc_template()
