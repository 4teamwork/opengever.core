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
            self._proposal.initial_position = data.get('initial_position')
            self._proposal.considerations = data.get('considerations')
            self._proposal.proposed_action = data.get('proposed_action')

        self._agenda_item.discussion = data.get('discussion')
        self._agenda_item.decision = data.get('decision')


class PreProtocolData(object):

    def __init__(self, meeting):
        self.meeting = meeting
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
        for agenda_item in self.meeting.agenda_items:
            if agenda_item.is_paragraph:
                continue

            pre_protocol = PreProtocol(agenda_item)
            self.data['agenda_items'].append({
                'number': pre_protocol.number,
                'description': pre_protocol.description,
                'title': pre_protocol.title,
                'initial_position': pre_protocol.initial_position,
                'proposed_action': pre_protocol.proposed_action,
                'considerations': pre_protocol.considerations,
                'discussion': pre_protocol.discussion,
                'decision': pre_protocol.decision,
            })

    def as_json(self):
        return json.dumps(self.data)
