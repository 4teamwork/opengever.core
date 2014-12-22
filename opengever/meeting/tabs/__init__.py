from five import grok
from opengever.tabbedview.browser.base import OpengeverTab
from opengever.tabbedview.browser.listing import ListingView
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from zope.interface import Interface


class BaseListingTab(grok.View, OpengeverTab, ListingView):
    """Base listing tab."""

    grok.context(Interface)
    grok.require('zope2.View')

    sort_on = 'modified'
    sort_reverse = False
    #lazy must be false otherwise there will be no correct batching
    lazy = False

    # the model attributes is used for a dynamic textfiltering functionality
    enabled_actions = []
    major_actions = []

    model = None

    # seems like grok cannot inherit these:
    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__


class BaseTableSource(SqlTableSource):

    grok.baseclass()

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
