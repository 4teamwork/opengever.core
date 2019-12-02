from opengever.meeting.model.agendaitem import AgendaItem  # noqa
from opengever.meeting.model.meeting import Meeting  # noqa
from opengever.meeting.model.committee import Committee  # noqa
from opengever.meeting.model.generateddocument import GeneratedExcerpt  # noqa
from opengever.meeting.model.generateddocument import GeneratedProtocol  # noqa
from opengever.meeting.model.member import Member  # noqa
from opengever.meeting.model.membership import Membership  # noqa
from opengever.meeting.model.proposal import Proposal  # noqa
from opengever.meeting.model.submitteddocument import SubmittedDocument  # noqa
from opengever.meeting.model.excerpt import Excerpt  # noqa
import opengever.meeting.model.query  # noqa


tables = [
    'agendaitems',
    'committees',
    'generateddocuments',
    'meeting_participants',
    'meetings',
    'members',
    'memberships',
    'proposals',
    'submitteddocuments',
    'excerpts',
]
