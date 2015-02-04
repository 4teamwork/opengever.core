from five import grok
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.meeting.tabs.committeelisting import CommitteeListingTab
from opengever.meeting.tabs.memberlisting import MemberListingTab


class Committees(CommitteeListingTab):
    grok.name('tabbedview_view-committees')
    grok.context(ICommitteeContainer)

    enabled_actions = []
    major_actions = []


class Members(MemberListingTab):
    grok.name('tabbedview_view-members')
    grok.context(ICommitteeContainer)

    enabled_actions = []
    major_actions = []
