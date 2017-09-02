from opengever.meeting.model.period import Period
from opengever.meeting.model.agendaitem import AgendaItem
from opengever.meeting.model.meeting import Meeting
from opengever.meeting.model.committee import Committee
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.model.generateddocument import GeneratedProtocol
from opengever.meeting.model.member import Member
from opengever.meeting.model.membership import Membership
from opengever.meeting.model.proposal import Proposal
from opengever.meeting.model.submitteddocument import SubmittedDocument
import opengever.meeting.model.query  # keep, initializes query classes!


tables = [
    'agendaitems',
    'committees',
    'generateddocuments',
    'meeting_excerpts',
    'meeting_participants',
    'meetings',
    'members',
    'memberships',
    'periods',
    'proposals',
    'submitteddocuments',
]
