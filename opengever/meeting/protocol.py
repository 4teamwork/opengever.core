from opengever.meeting import _
from opengever.ogds.base.utils import get_current_admin_unit
from zope.globalrequest import getRequest
from zope.i18n import translate
import json


class PreProtocolData(object):

    def __init__(self, meeting, agenda_items=None,
                 include_initial_position=True, include_legal_basis=True,
                 include_considerations=True, include_proposed_action=True,
                 include_discussion=True, include_decision=True):

        self.include_initial_position = include_initial_position
        self.include_legal_basis = include_legal_basis
        self.include_considerations = include_considerations
        self.include_proposed_action = include_proposed_action
        self.include_discussion = include_discussion
        self.include_decision = include_decision

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
                _(u'pre_protocol', default=u'Pre-Protocol'),
                context=getRequest())
        }

    def add_participants(self):
        participants = {
            'members': [
                participant.fullname for participant in
                self.meeting.participants
            ]
        }
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
                    include_decision=self.include_decision))

    def as_json(self):
        return json.dumps(self.data)


class ProtocolData(PreProtocolData):

    def add_protocol_type(self):
        self.data['protocol'] = {
            'type': translate(
                _(u'protocol', default=u'Protocol'),
                context=getRequest())
        }


class ExcerptProtocolData(object):

    def __init__(self, meeting, agenda_items):
        self.meeting = meeting
        self.agenda_items = agenda_items

        self.data = {}
        self.add_base()
        self.add_protocol_type()
        self.add_meeting()
        self.add_agenda_items()

    def add_base(self):
        self.data['mandant'] = {
            'name': get_current_admin_unit().title
        }

    def add_protocol_type(self):
        self.data['protocol'] = {
            'type': translate(
                _(u'protocol_excerpt', default=u'Protocol-Excerpt'),
                context=getRequest())
        }

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
                agenda_item.get_field_data())

    def as_json(self):
        return json.dumps(self.data)
