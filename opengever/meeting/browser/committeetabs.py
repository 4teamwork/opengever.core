from five import grok
from opengever.meeting.committee import ICommittee
from opengever.meeting.tabs.meetinglisting import MeetingListingTab
from opengever.meeting.tabs.submittedproposallisting import SubmittedProposalListingTab


class Meetings(MeetingListingTab):
    grok.name('tabbedview_view-meetings')
    grok.context(ICommittee)

    enabled_actions = []
    major_actions = []


class SubmittedProposals(SubmittedProposalListingTab):
    grok.name('tabbedview_view-submittedproposals')
    grok.context(ICommittee)

    enabled_actions = []
    major_actions = []
