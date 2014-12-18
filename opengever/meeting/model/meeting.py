from opengever.core.model import Base
from opengever.meeting import _
from opengever.meeting.model import AgendaItem
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Meeting(Base):

    PENDING = 'pending'
    CLOSED = 'closed'

    workflow_states = {
        PENDING: _('pending', default='Pending'),
        CLOSED: _('pending', default='Pending'),
    }

    __tablename__ = 'meetings'

    meeting_id = Column("id", Integer, Sequence("meeting_id_seq"),
                        primary_key=True)
    committee_id = Column(Integer, ForeignKey('committees.id'), nullable=False)
    committee = relationship("Committee", backref='meetings')
    location = Column(String(256))
    date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    workflow_state = Column(String(256), nullable=False, default=PENDING)

    def __repr__(self):
        return '<Meeting at "{}">'.format(self.date)

    def get_edit_values(self, fieldnames):
        # XXX this should be done in a more generic way by using either
        # the already present valueconverter stuff
        # or by registering our own converters based on column types
        values = {}
        for fieldname in fieldnames:
            value = getattr(self, fieldname, None)
            if not value:
                continue

            if fieldname == 'date':
                values['date-day'] = str(value.day)
                values['date-month'] = str(value.month)
                values['date-year'] = str(value.year)
                continue

            if fieldname in ['start_time', 'end_time']:
                value = value.strftime('%H:%M')
            values[fieldname] = value
        return values

    def update_model(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def get_title(self):
        return u"{} {}".format(self.committee.title,
                               self.date.strftime('%A, %d. %B %Y'))

    def get_workflow_state(self):
        return self.workflow_states.get(self.workflow_state)

    def schedule_proposal(self, proposal):
        assert proposal.committee == self.committee

        proposal.schedule(self)
        self.reorder_agenda_items()

    def schedule_text(self, title):
        self.agenda_items.append(AgendaItem(meeting=self, title=title))
        self.reorder_agenda_items()

    def reorder_agenda_items(self):
        sort_order = 1
        for agenda_item in self.agenda_items:
            agenda_item.sort_order = sort_order
            sort_order += 1
