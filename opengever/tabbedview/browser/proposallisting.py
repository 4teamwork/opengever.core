from five import grok
from ftw.table import helper
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.meeting.model.proposal import Proposal
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import OpengeverTab
from opengever.tabbedview.browser.listing import ListingView
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from zope.interface import implements
from zope.interface import Interface


def proposal_title(item, value):
    return item.get_link()


class IProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


class ProposalListingTab(grok.View, OpengeverTab, ListingView):
    """A tabbed view mixing which supports listing proposals.

    There is support for searching, batching and ordering.

    """
    implements(IProposalTableSourceConfig)
    grok.context(Interface)
    grok.require('zope2.View')

    sort_on = 'modified'
    sort_reverse = False
    #lazy must be false otherwise there will be no correct batching
    lazy = False

    # the model attributes is used for a dynamic textfiltering functionality
    model = Proposal
    enabled_actions = []
    major_actions = []

    columns = (
        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': proposal_title},

        {'column': 'initial_position',
         'column_title': _(u'column_initial_position',
                           default=u'Initial Position')},
        )

    # seems like grok cannot inherit these:
    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__


class ProposalTableSource(SqlTableSource):
    """Source adapter for Tasks we got from SQL
    """

    grok.implements(ITableSource)
    grok.adapts(ProposalListingTab, Interface)

    searchable_columns = [Proposal.title, Proposal.initial_position]

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.
        """
        # initalize config
        self.config.update_config()

        # get the base query from the config
        query = self.config.get_base_query()
        query = self.validate_base_query(query)

        return query
