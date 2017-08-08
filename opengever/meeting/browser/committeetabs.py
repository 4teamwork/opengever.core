from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.meeting.tabs.meetinglisting import MeetingListingTab
from opengever.meeting.tabs.membershiplisting import MembershipListingTab
from opengever.meeting.tabs.submittedproposallisting import SubmittedProposalListingTab
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class Meetings(MeetingListingTab):

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'start_datetime'

    enabled_actions = []
    major_actions = []


class SubmittedProposals(SubmittedProposalListingTab):

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    enabled_actions = []
    major_actions = []


class Memberships(MembershipListingTab):

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'member_id'

    enabled_actions = []
    major_actions = []

    def get_member_link(self, item, value):
        return item.member.get_link(aq_parent(aq_inner(self.context)))
