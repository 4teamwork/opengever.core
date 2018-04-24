from opengever.meeting import _
from opengever.meeting.model.membership import Membership
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
        self.add_settings()
        self.add_base()
        self.add_protocol_type()
        self.add_participants()
        self.add_meeting()
        self.add_commitee()
        self.add_agenda_items()

    def add_settings(self):
        if not self.meeting.protocol_start_page_number:
            return

        self.data['_sablon'] = {
            'properties': {
                'start_page_number': self.meeting.protocol_start_page_number
                }
            }

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
            if self.has_special_role(participant):
                continue

            membership = Membership.query.fetch_for_meeting(
                self.meeting, participant)
            members.append({
                "firstname": participant.firstname,
                "lastname": participant.lastname,
                "fullname": participant.fullname,
                "email": participant.email,
                "role": membership.role if membership else None
            })
        participants = {
            'members': members
        }

        return participants

    def has_special_role(self, participant):
        is_president = participant == self.meeting.presidency
        is_secretary = participant == self.meeting.secretary

        return is_president or is_secretary

    def add_participants(self):
        participants = self.add_members()
        if self.meeting.other_participants:
            other_participants = self.meeting.other_participants.split('\n')
        else:
            other_participants = []
        participants['other'] = other_participants

        if self.meeting.presidency:
            membership = Membership.query.fetch_for_meeting(
                self.meeting, self.meeting.presidency)
            participants['presidency'] = {
                "firstname": self.meeting.presidency.firstname,
                "lastname": self.meeting.presidency.lastname,
                "fullname": self.meeting.presidency.fullname,
                "email": self.meeting.presidency.email,
                "role": membership.role if membership else None
            }

        if self.meeting.secretary:
            participants['secretary'] = {
                "firstname": self.meeting.secretary.firstname,
                "lastname": self.meeting.secretary.lastname,
                "fullname": self.meeting.secretary.fullname(),
                "email": self.meeting.secretary.email,
            }

        self.data['participants'] = participants

    def add_meeting(self):
        self.data['meeting'] = {
            'date': self.meeting.get_date(),
            'start_time': self.meeting.get_start_time(),
            'end_time': self.meeting.get_end_time(),
            'number': self.meeting.meeting_number,
            'location': self.meeting.location,
        }

    def add_commitee(self):
        self.data['committee'] = {
            'name': self.meeting.committee.title,
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

    def as_json(self, pretty=False):
        indent = 4 if pretty else None
        return json.dumps(self.data, indent=indent)


class ExcerptProtocolData(ProtocolData):

    def add_protocol_type(self):
        self.data['protocol'] = {
            'type': translate(
                _(u'protocol_excerpt', default=u'Protocol-Excerpt'),
                context=getRequest())
        }

    def add_settings(self):
        """Do not add the start-page setting for excerpts."""
        pass


class AgendaItemListProtocolData(ProtocolData):

    def add_protocol_type(self):
        self.data['protocol'] = {
            'type': translate(
                _(u'label_agendaitem_list', default=u'Agendaitem list'),
                context=getRequest())
        }

    def add_settings(self):
        """Do not add the start-page setting for agendaitem lists."""
        pass
