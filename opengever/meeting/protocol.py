from opengever.meeting import _
from opengever.ogds.base.utils import get_current_admin_unit
from zope.globalrequest import getRequest
from zope.i18n import translate
import json


class PreProtocol(object):
    """Abstract from Proposal and AgendaItem for protocol-related attributes.

    Currently some attributes are available on a proposal wheras others are
    stored directly on an agenda_item.

    """
    def __init__(self, agenda_item):
        self._agenda_item = agenda_item
        self._proposal = self._agenda_item.proposal

    @property
    def has_proposal(self):
        return self._proposal is not None

    @property
    def legal_basis(self):
        return self._proposal.legal_basis if self.has_proposal else None

    @property
    def initial_position(self):
        return self._proposal.initial_position if self.has_proposal else None

    @property
    def considerations(self):
        return self._proposal.considerations if self.has_proposal else None

    @property
    def proposed_action(self):
        return self._proposal.proposed_action if self.has_proposal else None

    @property
    def discussion(self):
        return self._agenda_item.discussion

    @property
    def decision(self):
        return self._agenda_item.decision

    @property
    def name(self):
        return "preprotocols.{}".format(self._agenda_item.agenda_item_id)

    @property
    def title(self):
        return u"{} {}".format(self.number, self.description)

    @property
    def description(self):
        return self._agenda_item.get_title()

    @property
    def number(self):
        return self._agenda_item.number

    def update(self, request):
        """Update with changed data."""

        data = request.get(self.name)
        if not data:
            return

        if self.has_proposal:
            self._proposal.legal_basis = data.get('legal_basis')
            self._proposal.initial_position = data.get('initial_position')
            self._proposal.considerations = data.get('considerations')
            self._proposal.proposed_action = data.get('proposed_action')

        self._agenda_item.discussion = data.get('discussion')
        self._agenda_item.decision = data.get('decision')

    def get_field_data(self, include_initial_position=True,
                       include_legal_basis=True, include_considerations=True,
                       include_proposed_action=True, include_discussion=True,
                       include_decision=True):
        data = {
            'number': self.number,
            'description': self.description,
            'title': self.title,
        }
        if include_initial_position:
            data['markdown:initial_position'] = self._sanitize_text(
                self.initial_position)
        if include_legal_basis:
            data['markdown:legal_basis'] = self._sanitize_text(
                self.legal_basis)
        if include_considerations:
            data['markdown:considerations'] = self._sanitize_text(
                self.considerations)
        if include_proposed_action:
            data['markdown:proposed_action'] = self._sanitize_text(
                self.proposed_action)
        if include_discussion:
            data['markdown:discussion'] = self._sanitize_text(self.discussion)
        if include_decision:
            data['markdown:decision'] = self._sanitize_text(self.decision)

        return data

    def _sanitize_text(self, text):
        if not text:
            return None

        return text


class PreProtocolData(object):

    def __init__(self, meeting, pre_protocols=None,
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
        if pre_protocols:
            self.pre_protocols = pre_protocols
        else:
            self.pre_protocols = []
            for agenda_item in self.meeting.agenda_items:
                if agenda_item.is_paragraph:
                    continue
                self.pre_protocols.append(PreProtocol(agenda_item))

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
        for pre_protocol in self.pre_protocols:
            self.data['agenda_items'].append(
                pre_protocol.get_field_data(
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
                PreProtocol(agenda_item).get_field_data())

    def as_json(self):
        return json.dumps(self.data)
