from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.model import Proposal
from opengever.meeting.tabs import BaseListingTab
from opengever.meeting.tabs import BaseTableSource
from opengever.tabbedview import _
from zope.interface import implements
from zope.interface import Interface


def proposal_link(item, value):
    return item.get_link()


class IProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


class ProposalListingTab(BaseListingTab):
    implements(IProposalTableSourceConfig)

    model = Proposal

    columns = (
        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': proposal_link},

        {'column': 'initial_position',
         'column_title': _(u'column_initial_position',
                           default=u'Initial Position')},
        )


class ProposalTableSource(BaseTableSource):
    grok.implements(ITableSource)
    grok.adapts(ProposalListingTab, Interface)

    searchable_columns = [Proposal.title, Proposal.initial_position]
