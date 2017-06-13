from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.model import Proposal
from opengever.meeting.tabs.proposallisting import ProposalListingTab
from opengever.tabbedview import SqlTableSource
from zope.interface import implements
from zope.interface import Interface


def proposal_title_link(item, value):
    return item.get_submitted_link()


class ISubmittedProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for submitted proposal table source configs."""


class SubmittedProposalListingTab(ProposalListingTab):
    implements(ISubmittedProposalTableSourceConfig)

    sort_on = ''

    def get_base_query(self):
        return Proposal.query.visible_for_committee(
            self.context.load_model())

    @property
    def columns(self):
        """Inherit column definition from the ProposalListingTab,
        but replace transform with """

        columns = super(SubmittedProposalListingTab, self).columns
        for col in columns:
            if col.get('column') == 'title':
                col['transform'] = proposal_title_link

        return columns


class SubmittedProposalTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(SubmittedProposalListingTab, Interface)

    searchable_columns = []
