"""
This module contains the tabbed views and all the stuff used in the Async
control panel.
"""

from five import grok
from ftw.tabbedview.browser.listing import ListingView
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.tabbedview import _
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import queue_view_helper
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.app.component.hooks import setSite
from zope.interface import implements, Interface
import zc.async.interfaces


class IAsyncTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using a
    listing of zc.async queues as source.
    """


class QueueListingTab(grok.CodeView, OpengeverTab, ListingView):
    """A tabbed view mixin which brings support for listing zc.async
    queues persisted in the ZODB.

    There is no support for searching, batching or ordering yet.
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


class AsyncControlPanel(grok.View, TabbedView):
    """zc.async control panel tabbed view.
    """
    grok.context(IPloneSiteRoot)
    grok.name('async-controlpanel')
    grok.require('cmf.ManagePortal')

    tabs = [
        {'id': 'async-queues',
         'icon': None,
         'url': '#',
         'class': None},

        {'id': 'settings',
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


class AsyncAllQueues(QueueListingTab):
    """Lists all zc.async queues.
    """

    grok.context(IPloneSiteRoot)
    grok.name('tabbedview_view-async-queues')
    grok.require('cmf.ManagePortal')

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        context = self.context
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        setSite(portal)
        conn = portal._p_jar
        root = conn.root()
        queues = root[zc.async.interfaces.KEY]
        query = []
        for k, v in queues.items():
            if k == '':
                k = 'DEFAULT'
            query.append({'name':k,'length':len(v)})
        return query


class AsyncTableSource(grok.MultiAdapter, BaseTableSource):
    """Table source adapter for zc.async queues.
    """

    grok.implements(ITableSource)
    grok.adapts(IAsyncTableSourceConfig, Interface)

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

