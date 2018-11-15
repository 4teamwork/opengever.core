from datetime import datetime
from opengever.meeting import _
from opengever.meeting.model.membership import Membership
from opengever.meeting.utils import format_date
from opengever.meeting.utils import JsonDataProcessor
from opengever.ogds.base.utils import get_current_admin_unit
from zope.globalrequest import getRequest
from zope.i18n import translate
import copy
import json


class ProtocolData(object):

    def __init__(self, meeting, agenda_items=None):
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
        self.add_general_metadata()

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

    @staticmethod
    def get_member_data(member, membership=None):
        return {"firstname": member.firstname,
                "lastname": member.lastname,
                "fullname": member.fullname,
                "email": member.email,
                "role": membership.role if membership else None}

    def get_attending_members(self):
        members = []
        for participant in self.meeting.participants:
            if self.has_special_role(participant):
                continue

            membership = Membership.query.fetch_for_meeting(
                self.meeting, participant)
            members.append(self.get_member_data(participant, membership))
        return members

    def get_absent_members(self):
        # Now we add the members that are not attending the meeting
        absentees = []
        for absentee in self.meeting.absentees:
            membership = Membership.query.fetch_for_meeting(
                    self.meeting, absentee)
            absentees.append(self.get_member_data(absentee, membership))
        return absentees

    def has_special_role(self, participant):
        is_president = participant == self.meeting.presidency
        is_secretary = participant == self.meeting.secretary

        return is_president or is_secretary

    def add_participants(self):
        participants = {}
        participants['members'] = self.get_attending_members()
        if self.meeting.other_participants:
            other_participants = self.meeting.other_participants.split('\n')
        else:
            other_participants = []
        participants['other'] = other_participants

        participants['absentees'] = self.get_absent_members()

        if self.meeting.presidency:
            membership = Membership.query.fetch_for_meeting(
                self.meeting, self.meeting.presidency)
            participants['presidency'] = self.get_member_data(
                self.meeting.presidency, membership)

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
            'date': self.meeting.start,
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
                agenda_item.get_agenda_item_data())

    def add_general_metadata(self):
        self.data['document'] = {
            'generated': datetime.now(),
        }

    def as_json(self, pretty=False):
        indent = 4 if pretty else None
        return json.dumps(self.get_processed_data(), indent=indent)

    def get_processed_data(self):
        data_fields = (("meeting", "date"), ("document", "generated"))
        transforms = (format_date for field in data_fields)
        processed_data = copy.deepcopy(self.data)
        processor = JsonDataProcessor()
        return processor.process(processed_data, data_fields, transforms)


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
