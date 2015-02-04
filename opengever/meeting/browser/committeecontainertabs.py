from five import grok
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.meeting.tabs.memberlisting import MemberListingTab


class Members(MemberListingTab):
    grok.name('tabbedview_view-members')
    grok.context(ICommitteeContainer)

    enabled_actions = []
    major_actions = []
