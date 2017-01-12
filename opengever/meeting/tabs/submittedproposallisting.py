from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Proposal
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.browser.tabs import Proposals
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


def proposal_title_link(item, value):
    return item.get_submitted_link()


class ISubmittedProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for submitted proposal table source configs."""


class AllProposalFilter(Filter):

    visible_states = ['submitted', 'scheduled', 'decided']

    def update_query(self, query):
        return query.filter(Proposal.workflow_state.in_(self.visible_states))


class UndecidedProposalFilter(AllProposalFilter):

    visible_states = ['submitted', 'scheduled']


class DecidedProposalFilter(AllProposalFilter):

    visible_states = ['decided']


class SubmittedProposalListingTab(Proposals):
    implements(ISubmittedProposalTableSourceConfig)

    filterlist_name = 'submitted_proposal_state_filter'
    filterlist = FilterList(
        AllProposalFilter('filter_proposals_all',
                          _('all', default=u'All')),
        UndecidedProposalFilter(
            'filter_proposals_active',
            _('active', default=u'Active'),
            default=True),
        DecidedProposalFilter('filter_proposals_decided',
                              _('decided', default=u'Decided'))
    )

    def get_base_query(self):
        return Proposal.query.for_committee(self.context.load_model())

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


@implementer(ITableSource)
@adapter(ISubmittedProposalTableSourceConfig, Interface)
class SubmittedProposalTableSource(SqlTableSource):

    searchable_columns = []
