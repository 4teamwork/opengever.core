from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.browser.documents.proposalstab import ProposalListingTab
from opengever.meeting.model import Proposal
from opengever.meeting.tabs.meetinglisting import MeetingListingTab
from opengever.meeting.tabs.membershiplisting import MembershipListingTab
from opengever.tabbedview import SqlTableSource
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class Meetings(MeetingListingTab):

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'start_datetime'

    enabled_actions = []
    major_actions = []


class Memberships(MembershipListingTab):

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'member_id'

    enabled_actions = []
    major_actions = []

    def get_member_link(self, item, value):
        return item.member.get_link(aq_parent(aq_inner(self.context)))


class ISubmittedProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for submitted proposal table source configs."""


@implementer(ITableSource)
@adapter(ISubmittedProposalTableSourceConfig, Interface)
class SubmittedProposalTableSource(SqlTableSource):

    searchable_columns = []


def proposal_title_link(item, value):
    return item.get_submitted_link()


class SubmittedProposalListingTab(ProposalListingTab):
    implements(ISubmittedProposalTableSourceConfig)

    def get_base_query(self):
        return Proposal.query.visible_for_committee(self.context.load_model())

    @property
    def columns(self):
        """Inherit column definition from the ProposalListingTab,
        but replace transform.
        """
        columns = super(SubmittedProposalListingTab, self).columns
        for col in columns:
            if col.get('column') == 'title':
                col['transform'] = proposal_title_link

        return columns
