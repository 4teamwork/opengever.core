from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Proposal
from opengever.meeting.tabs.proposallisting import ProposalListingTab
from opengever.tabbedview.browser.base import BaseTableSource
from zope.interface import implements
from zope.interface import Interface


def proposal_title(item, value):
    return item.get_submitted_link()


class ISubmittedProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


class SubmittedProposalListingTab(ProposalListingTab):
    implements(ISubmittedProposalTableSourceConfig)

    def get_base_query(self):
        return Proposal.query.visible_for_committee(
            self.context.load_model())

    columns = (
        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': proposal_title},

        {'column': 'initial_position',
         'column_title': _(u'column_initial_position',
                           default=u'Initial Position')},
        )


class SubmittedProposalTableSource(BaseTableSource):
    grok.implements(ITableSource)
    grok.adapts(SubmittedProposalListingTab, Interface)

    searchable_columns = [Proposal.title, Proposal.initial_position]
