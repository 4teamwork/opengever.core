from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.browser.documents.proposalstab import ProposalListingTab
from opengever.meeting.model import Proposal
from opengever.meeting.tabs.meetinglisting import MeetingListingTab
from opengever.meeting.tabs.membershiplisting import MembershipListingTab
from opengever.tabbedview import SqlTableSource
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class Meetings(MeetingListingTab):
    pass


class Memberships(MembershipListingTab):
    pass


class ISubmittedProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for submitted proposal table source configs."""


@implementer(ITableSource)
@adapter(ISubmittedProposalTableSourceConfig, Interface)
class SubmittedProposalTableSource(SqlTableSource):

    searchable_columns = [Proposal.submitted_title]


def proposal_title_link(item, value):
    return item.get_submitted_link()


def get_submitted_description(item, value):
    """XSS safe submitted description"""
    return item.get_submitted_description()


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
            elif col.get('column') == 'description':
                col['transform'] = get_submitted_description

        return columns
