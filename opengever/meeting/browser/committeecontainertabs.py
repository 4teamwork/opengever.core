from five import grok
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.meeting.service import meeting_service
from opengever.meeting.tabs.memberlisting import MemberListingTab
from opengever.tabbedview.browser.base import OpengeverTab
from zope.app.pagetemplate import ViewPageTemplateFile


class Committees(grok.View, OpengeverTab):
    grok.name('tabbedview_view-committees')
    grok.context(ICommitteeContainer)
    grok.require('zope2.View')
    grok.template('committee')

    def committees(self):
        committees = []

        filter = self.request.form.get('searchable_text', None)
        for committee in meeting_service().all_committees(text_filter=filter):
            committees.append(
                {'title': committee.title,
                 'url': committee.get_url(),
                 'number_unscheduled_proposals': len(
                     meeting_service().get_submitted_proposals(committee)),
                 'next_meeting': meeting_service().get_next_meeting(committee),
                 'last_meeting': meeting_service().get_last_meeting(committee)}
            )

        return committees


class Members(MemberListingTab):
    grok.name('tabbedview_view-members')
    grok.context(ICommitteeContainer)

    selection = ViewPageTemplateFile("templates/no_selection.pt")
    sort_on = 'lastname'

    enabled_actions = []
    major_actions = []
