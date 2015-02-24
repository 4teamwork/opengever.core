from five import grok
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.meeting.tabs.committeelisting import CommitteeListingTab
from opengever.meeting.tabs.memberlisting import MemberListingTab
from zope.app.pagetemplate import ViewPageTemplateFile


class Committees(CommitteeListingTab):
    grok.name('tabbedview_view-committees')
    grok.context(ICommitteeContainer)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    enabled_actions = []
    major_actions = []


class Members(MemberListingTab):
    grok.name('tabbedview_view-members')
    grok.context(ICommitteeContainer)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    enabled_actions = []
    major_actions = []
