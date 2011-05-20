"""
This module contains the tabbed views and all the stuff used in the Async
control panel.
"""

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab

from five import grok
from sqlalchemy import or_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import asc, desc
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import implements, Interface

from ftw.journal.interfaces import IJournalizable
from ftw.tabbedview.browser.listing import ListingView
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.base.browser.helper import client_title_helper
from opengever.globalindex.model.task import Task
from opengever.globalindex.utils import indexed_task_link_helper
from opengever.tabbedview import _
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import overdue_date_helper
from opengever.tabbedview.helper import readable_date
from opengever.tabbedview.helper import readable_date_set_invisibles
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import task_id_checkbox_helper
from opengever.tabbedview.helper import workflow_state
from opengever.task.helper import task_type_helper
import zc.async.interfaces
from zope.app.component.hooks import setSite
from Products.CMFCore.utils import getToolByName
from opengever.tabbedview.helper import queue_view_helper

class IAsyncTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using the
    `opengever.globalindex` as source.
    """


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


class AsyncAllTasks(QueueListingTab):
    """Lists all tasks in the globalindex.
    """

    grok.context(IPloneSiteRoot)
    grok.name('tabbedview_view-async-queues')
    grok.require('cmf.ManagePortal')

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        context = self.context
        catalog = context.portal_catalog
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        setSite(portal)
        conn = portal._p_jar
        root = conn.root()
        queues = root[zc.async.interfaces.KEY]
        query = []
        for k, v in queues.items():
            query.append({'name':k,'length':len(v)})
        return query


class AsyncTableSource(grok.MultiAdapter, BaseTableSource):
    """Base table source adapter.
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

