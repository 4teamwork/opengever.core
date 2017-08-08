from five import grok
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.meeting.model import Committee
from opengever.meeting.model import Meeting
from opengever.meeting.service import meeting_service
from opengever.meeting.tabs.memberlisting import MemberListingTab
from opengever.tabbedview import GeverTabMixin
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview import _ as tmf
from plone import api
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class ActiveOnlyFilter(Filter):
    def update_query(self, query):
        return query.active()


class Committees(grok.View, GeverTabMixin):
    grok.name('tabbedview_view-committees')
    grok.context(ICommitteeContainer)
    grok.require('zope2.View')
    grok.template('committee')

    filterlist_name = 'committee_state_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', tmf('all')),
        ActiveOnlyFilter('filter_active', tmf('Active'), default=True))

    def __call__(self):
        self.selected_filter_id = self.request.get(self.filterlist_name)
        return super(Committees, self).__call__()

    def extend_query_with_statefilter(self, query):
        return self.filterlist.update_query(
            query,
            self.request.get(self.filterlist_name))

    def committees(self):
        committees = []
        filter = self.get_filter_text()
        query = Committee.query.order_by(Committee.title)
        query = query.by_searchable_text(text_filters=filter)
        query = self.extend_query_with_statefilter(query)

        for committee in query.all():
            content_obj = committee.resolve_committee()
            if not content_obj:
                continue
            if not api.user.has_permission('View', obj=content_obj):
                continue

            committees.append(
                {'title': committee.title,
                 'url': committee.get_url(),
                 'state_class': 'active' if committee.is_active() else 'inactive',
                 'number_unscheduled_proposals': len(
                     meeting_service().get_submitted_proposals(committee)),
                 'next_meeting': Meeting.query.get_next_meeting(committee),
                 'last_meeting': Meeting.query.get_last_meeting(committee)}
            )

        return committees


class Members(MemberListingTab):

    selection = ViewPageTemplateFile("templates/no_selection.pt")
    sort_on = 'lastname'

    enabled_actions = []
    major_actions = []
