from opengever.base.model import Base
from opengever.meeting import _
from opengever.meeting.model import AgendaItem
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from plone import api
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Meeting(Base):

    STATE_PENDING = State('pending', is_default=True,
                          title=_('pending', default='Pending'))
    STATE_HELD = State('held', title=_('held', default='Held'))
    STATE_CLOSED = State('closed', title=_('closed', default='Closed'))

    workflow = Workflow([
        STATE_PENDING,
        STATE_HELD,
        STATE_CLOSED,
        ], [
        Transition('pending', 'held',
                   title=_('hold meeting', default='Hold meeting')),
        Transition('held', 'closed',
                   title=_('close', default='Close')),
        ])

    __tablename__ = 'meetings'

    meeting_id = Column("id", Integer, Sequence("meeting_id_seq"),
                        primary_key=True)
    committee_id = Column(Integer, ForeignKey('committees.id'), nullable=False)
    committee = relationship("Committee", backref='meetings')
    location = Column(String(256))
    date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    workflow_state = Column(String(256), nullable=False,
                            default=workflow.default_state.name)

    def __repr__(self):
        return '<Meeting at "{}">'.format(self.date)

    def is_editable(self):
        return self.get_state() == self.STATE_PENDING

    @property
    def physical_path(self):
        return '/'.join(
            (self.committee.physical_path, 'meeting', str(self.meeting_id)))

    def execute_transition(self, name):
        self.workflow.execute_transition(self, self, name)

    def can_execute_transition(self, name):
        return self.workflow.can_execute_transition(self, name)

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

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
        return u"{} {}".format(self.committee.title, self.get_date())

    def get_date(self):
        return self.date.strftime('%A, %d. %B %Y')

    def get_start_time(self):
        return self.start_time.strftime('%H:%M') if self.start_time else ''

    def get_end_time(self):
        return self.end_time.strftime('%H:%M') if self.end_time else ''

    def schedule_proposal(self, proposal):
        assert proposal.committee == self.committee

        proposal.schedule(self)
        self.reorder_agenda_items()

    def schedule_text(self, title):
        self.agenda_items.append(AgendaItem(title=title))
        self.reorder_agenda_items()

    def schedule_paragraph(self, title):
        self.agenda_items.append(AgendaItem(title=title, is_paragraph=True))
        self.reorder_agenda_items()

    def reorder_agenda_items(self):
        sort_order = 1
        number = 1
        for agenda_item in self.agenda_items:
            agenda_item.sort_order = sort_order
            sort_order += 1
            if not agenda_item.is_paragraph:
                agenda_item.number = '{}.'.format(number)
                number += 1

    def get_submitted_link(self):
        return self._get_link(self.get_submitted_admin_unit(),
                              self.submitted_physical_path)

    def get_link(self):
        url = self.get_url()
        link = u'<a href="{0}" title="{1}">{1}</a>'.format(url, self.get_title())

        transformer = api.portal.get_tool('portal_transforms')
        return transformer.convertTo('text/x-html-safe', link).getData()

    def get_url(self):
        admin_unit = self.committee.get_admin_unit()
        return '/'.join((admin_unit.public_url, self.physical_path))

    def get_edit_url(self):
        return '/'.join((self.get_url(), 'edit'))

    def get_breadcrumbs(self):
        return {'absolute_url': self.get_url(), 'Title': self.get_title()}
