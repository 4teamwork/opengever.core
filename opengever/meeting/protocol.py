from opengever.meeting import _
from opengever.meeting.model import Membership
from opengever.ogds.base.utils import get_current_admin_unit
from zope.globalrequest import getRequest
from zope.i18n import translate
import json


class ProtocolData(object):

    def __init__(self, meeting, agenda_items=None,
                 include_initial_position=True, include_legal_basis=True,
                 include_considerations=True, include_proposed_action=True,
                 include_discussion=True, include_decision=True,
                 include_publish_in=True, include_disclose_to=True,
                 include_copy_for_attention=True):

        self.include_initial_position = include_initial_position
        self.include_legal_basis = include_legal_basis
        self.include_considerations = include_considerations
        self.include_proposed_action = include_proposed_action
        self.include_discussion = include_discussion
        self.include_decision = include_decision
        self.include_publish_in = include_publish_in
        self.include_disclose_to = include_disclose_to
        self.include_copy_for_attention = include_copy_for_attention

        self.meeting = meeting
        self.agenda_items = agenda_items or self.meeting.agenda_items

        self.data = {}
        self.add_base()
        self.add_protocol_type()
        self.add_participants()
        self.add_meeting()
        self.add_agenda_items()

    def add_base(self):
        self.data['mandant'] = {
            'name': get_current_admin_unit().title
        }

    def add_protocol_type(self):
        self.data['protocol'] = {
            'type': translate(
                _(u'protocol', default=u'Protocol'),
                context=getRequest())
        }

    def add_members(self):
        members = []
        for participant in self.meeting.participants:
            membership = Membership.query.fetch_for_meeting(
                self.meeting, participant)
            if membership.role:
                members.append(u"{}, {}".format(
                    participant.fullname, membership.role))
            else:
                members.append(participant.fullname)

        participants = {
            'members': members
        }
        return participants

    def add_participants(self):
        participants = self.add_members()
        if self.meeting.other_participants:
            other_participants = self.meeting.other_participants.split('\n')
        else:
            other_participants = []
        participants['other'] = other_participants

        if self.meeting.presidency:
            participants['presidency'] = self.meeting.presidency.fullname
        if self.meeting.secretary:
            participants['secretary'] = self.meeting.secretary.fullname

        self.data['participants'] = participants

    def add_meeting(self):
        self.data['meeting'] = {
            'date': self.meeting.get_date(),
            'start_time': self.meeting.get_start_time(),
            'end_time': self.meeting.get_end_time(),
        }

    def add_agenda_items(self):
        self.data['agenda_items'] = []
        for agenda_item in self.agenda_items:
            self.data['agenda_items'].append(
                agenda_item.get_field_data(
                    include_initial_position=self.include_initial_position,
                    include_legal_basis=self.include_legal_basis,
                    include_considerations=self.include_considerations,
                    include_proposed_action=self.include_proposed_action,
                    include_discussion=self.include_discussion,
                    include_decision=self.include_decision,
                    include_publish_in=self.include_publish_in,
                    include_disclose_to=self.include_disclose_to,
                    include_copy_for_attention=self.include_copy_for_attention
                ))

    def as_json(self):
        return json.dumps(self.data)


class ExcerptProtocolData(ProtocolData):

    def add_protocol_type(self):
        self.data['protocol'] = {
            'type': translate(
                _(u'protocol_excerpt', default=u'Protocol-Excerpt'),
                context=getRequest())
        }
