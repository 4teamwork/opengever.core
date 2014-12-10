from five import grok
from opengever.meeting.form import MeetingModelEditForm
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import Proposal
from plone.directives import dexterity
from z3c.form import field


class EditForm(MeetingModelEditForm, dexterity.EditForm):

    grok.context(IProposal)
    fields = field.Fields(Proposal.model_schema, ignoreContext=True)
    content_type = Proposal
