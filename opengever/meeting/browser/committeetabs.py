from five import grok
from opengever.meeting import _
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Proposal
from opengever.meeting.tabs.meetinglisting import MeetingListingTab
from opengever.meeting.tabs.membershiplisting import MembershipListingTab
from opengever.meeting.tabs.proposallisting import translated_state
from opengever.meeting.tabs.submittedproposallisting import proposal_title_link
from opengever.meeting.tabs.submittedproposallisting import SubmittedProposalListingTab
from zope.app.pagetemplate import ViewPageTemplateFile


class Meetings(MeetingListingTab):
    grok.name('tabbedview_view-meetings')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'start'

    enabled_actions = []
    major_actions = []


class SubmittedProposals(SubmittedProposalListingTab):
    grok.name('tabbedview_view-submittedproposals')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    enabled_actions = []
    major_actions = []


class DecidedProposals(SubmittedProposalListingTab):
    grok.name('tabbedview_view-decidedproposals')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    enabled_actions = []
    major_actions = []

    columns = (
        {'column': 'proposal_id',
         'column_title': _(u'column_number', default=u'Nr.')},

        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': proposal_title_link},

        {'column': 'workflow_state',
         'column_title': _(u'column_state', default=u'State'),
         'transform': translated_state},

        {'column': 'committee_id',
         'column_title': _(u'column_comittee', default=u'Comittee'),
         'transform': lambda item, value: item.committee.title},

        {'column': 'initial_position',
         'column_title': _(u'column_initial_position',
                           default=u'Initial Position')},

        {'column': 'proposed_action',
         'column_title': _(u'column_proposed_action',
                           default=u'Proposed action')},

        {'column': 'decision',
         'column_title': _(u'column_decision', default=u'Decision'),
         'transform': lambda item, value: item.get_decision()},
    )

    def get_base_query(self):
        return Proposal.query.decided_by_committee(self.context.load_model())


class Memberships(MembershipListingTab):
    grok.name('tabbedview_view-memberships')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'member_id'

    enabled_actions = []
    major_actions = []
