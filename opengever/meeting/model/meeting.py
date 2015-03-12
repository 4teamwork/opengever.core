from collections import OrderedDict
from opengever.base.model import Base
from opengever.meeting import _
from opengever.meeting.model import AgendaItem
from opengever.meeting.model.query import MeetingQuery
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from plone import api
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


meeting_participants = Table(
    'meeting_participants', Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id')),
    Column('member_id', Integer, ForeignKey('members.id'))
)


class Meeting(Base):

    query_cls = MeetingQuery

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
    start = Column(DateTime, nullable=False)
    end = Column(DateTime)
    workflow_state = Column(String(256), nullable=False,
                            default=workflow.default_state.name)

    presidency = relationship(
        'Member', primaryjoin="Member.member_id==Meeting.presidency_id")
    presidency_id = Column(Integer, ForeignKey('members.id'))
    secretary = relationship(
        'Member', primaryjoin="Member.member_id==Meeting.secretary_id")
    secretary_id = Column(Integer, ForeignKey('members.id'))
    other_participants = Column(Text)
    participants = relationship('Member',
                                secondary=meeting_participants,
                                backref='meetings')

    agenda_items = relationship("AgendaItem", order_by='AgendaItem.sort_order')

    pre_protocol_document_id = Column(
        Integer, ForeignKey('generateddocuments.id'))
    pre_protocol_document = relationship(
        'GeneratedPreProtocol', uselist=False,
        backref=backref('meeting', uselist=False),
        primaryjoin="GeneratedPreProtocol.document_id==Meeting.pre_protocol_document_id")
    protocol_document_id = Column(Integer, ForeignKey('generateddocuments.id'))
    protocol_document = relationship(
        'GeneratedProtocol', uselist=False,
        backref=backref('meeting', uselist=False),
        primaryjoin="GeneratedProtocol.document_id==Meeting.protocol_document_id")

    def __repr__(self):
        return '<Meeting at "{}">'.format(self.start)

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

            if fieldname in ['start', 'end']:
                values['{}-day'.format(fieldname)] = str(value.day)
                values['{}-month'.format(fieldname)] = str(value.month)
                values['{}-year'.format(fieldname)] = str(value.year)
                values['{}-hour'.format(fieldname)] = str(value.hour)
                values['{}-min'.format(fieldname)] = str(value.minute)
                continue

            values[fieldname] = value
        return values

    def update_model(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def get_title(self):
        if self.location:
            return u"{}, {}".format(self.location, self.get_date())
        else:
            return self.get_date()

    def get_date(self):
        return api.portal.get_localized_time(datetime=self.start)

    def get_start_time(self):
        return self._get_localized_time(self.start)

    def get_end_time(self):
        return self._get_localized_time(self.end)

    def _get_localized_time(self, date):
        if not date:
            return ''

        return api.portal.get_localized_time(datetime=date, time_only=True)

    def schedule_proposal(self, proposal):
        assert proposal.committee == self.committee

        proposal.schedule(self)
        self.reorder_agenda_items()

    def schedule_text(self, title, is_paragraph=False):
        self.agenda_items.append(AgendaItem(title=title,
                                            is_paragraph=is_paragraph))
        self.reorder_agenda_items()

    def _set_agenda_item_order(self, new_order):
        agenda_items_by_id = OrderedDict((item.agenda_item_id, item)
                                         for item in self.agenda_items)
        agenda_items = []

        for agenda_item_id in new_order:
            agenda_item = agenda_items_by_id.pop(agenda_item_id, None)
            if agenda_item:
                agenda_items.append(agenda_item)
        agenda_items.extend(agenda_items_by_id.values())
        self.agenda_items = agenda_items

    def reorder_agenda_items(self, new_order=None):
        if new_order:
            self._set_agenda_item_order(new_order)

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

    def get_edit_url(self, context):
        return '/'.join((self.get_url(), 'edit'))

    def get_breadcrumbs(self, context):
        return {'absolute_url': self.get_url(), 'Title': self.get_title()}
