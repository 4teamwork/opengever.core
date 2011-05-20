from ftw.table.interfaces import ITableSource, ITableSourceConfig
from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.table.basesource import BaseTableSource
from zope.interface import implements, Interface


class IJoblistingSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using the
    `opengever.globalindex` as source.
    """

    class AsyncControlPanel(grok.View, TabbedView):
        """zc.async control panel tabbed view.
        """

        grok.context(IPloneSiteRoot)
        grok.name('jobs_view')
        grok.require('cmf.ManagePortal')

        tabs = [
            {'id': 'jobs',
             'icon': None,
             'url': '#',
             'class': None},


            ]

        def __init__(self, *args, **kwargs):
            grok.View.__init__(self, *args, **kwargs)
            TabbedView.__init__(self, *args, **kwargs)

        def get_tabs(self):
            return self.tabs

        def render(self):
            return TabbedView.__call__(self)


class QueueListingTab(grok.CodeView, OpengeverTab,
                           ListingView):
    """A tabbed view mixing which brings support for listing tasks from
    the SQL (globally over all clients).

    There is support for searching, batching and ordering.
    """

    implements(IAsyncTableSourceConfig)

    grok.context(Interface)

    sort_on = 'name'
    sort_reverse = False

    enabled_actions = []
    major_actions = []

    columns = (

        {'column': 'name',
         'column_title': _(u'column_name', default=u'Name'),
         'transform': queue_view_helper
         },

        {'column': 'length',
         'column_length': _(u'column_length', default=u'Length'),
         },

        )


    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__



    class JoblistingTableSource(grok.MultiAdapter, BaseTableSource):
        """Base table source adapter.
        """

        grok.implements(ITableSource)
        grok.adapts(IJoblistingSourceConfig, Interface)

        def validate_base_query(self, query):
            """Validates and fixes the base query. Returns the query object.
            It may raise e.g. a `ValueError` when something's wrong.
            """
            return query

        def extend_query_with_ordering(self, query):
            """Extends the given `query` with ordering information and returns
            the new query.
            """
            return query

        def extend_query_with_textfilter(self, query, text):
            """Extends the given `query` with text filters. This is only done when
            config's `filter_text` is set.
            """

            return query

        def extend_query_with_batching(self, query):
            """Extends the given `query` with batching filters and returns the
            new query. This method is only called when batching is enabled in
            the source config with the `batching_enabled` attribute.
            """

            return query

        def search_results(self, query):
            """Executes the query and returns a tuple of `results`.
            """

            return query
