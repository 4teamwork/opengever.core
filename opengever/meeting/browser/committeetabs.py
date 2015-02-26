from five import grok
from opengever.meeting.committee import ICommittee
from opengever.meeting.tabs.meetinglisting import MeetingListingTab
from opengever.meeting.tabs.membershiplisting import MembershipListingTab
from opengever.meeting.tabs.submittedproposallisting import SubmittedProposalListingTab
from zope.app.pagetemplate import ViewPageTemplateFile


class Meetings(MeetingListingTab):
    grok.name('tabbedview_view-meetings')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'date'

    enabled_actions = []
    major_actions = []


class SubmittedProposals(SubmittedProposalListingTab):
    grok.name('tabbedview_view-submittedproposals')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    enabled_actions = []
    major_actions = []


class Memberships(MembershipListingTab):
    grok.name('tabbedview_view-memberships')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'member_id'

    enabled_actions = []
    major_actions = []
