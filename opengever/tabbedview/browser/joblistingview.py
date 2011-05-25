from five import grok
from ftw.tabbedview.browser.listing import ListingView
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.tabbedview import _
from opengever.tabbedview.browser.tabs import OpengeverTab
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ZODB.utils import u64
from zope.app.component.hooks import getSite
from zope.app.component.hooks import setSite
from zope.interface import implements, Interface
import zc.async


def linked_document(item, value):
    portal = getSite()
    catalog = portal.portal_catalog
    doc_path = '/'.join(value)
    document = catalog(path=doc_path)[0]
    item = document
    value = document.Title

    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    img = '<img src="%s/%s"/>' % (item.portal_url(),
                                  item.getIcon.encode('utf-8'))

    breadcrumb_titles = []
    for elem in item.breadcrumb_titles:
        if isinstance(elem.get('Title'), unicode):
            breadcrumb_titles.append(elem.get('Title').encode('utf-8'))
        else:
            breadcrumb_titles.append(elem.get('Title'))
    link = '%s&nbsp;<a class="rollover-breadcrumb" href="%s" title="%s">%s</a>' % (
        img, url_method(),
        " &gt; ".join(t for t in breadcrumb_titles),
        value.encode('utf-8'))
    wrapper = '<span class="linkWrapper">%s</span>' % link
    return wrapper



class IJoblistingSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using the
    zc.async jobs as source.
    """


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


class JobsView(grok.View, TabbedView):
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


class JobListingTab(grok.CodeView, OpengeverTab,
                           ListingView):
    """A tabbed view mixing which brings support for listing tasks from
    the SQL (globally over all clients).

    There is support for searching, batching and ordering.
    """

    implements(IJoblistingSourceConfig)

    grok.context(Interface)
    grok.name('tabbedview_view-jobs')

    sort_on = 'name'
    sort_reverse = False

    enabled_actions = []
    major_actions = []

    columns = (

            {'column': 'position',
            'column_title': _(u'column_position', default=u'Position'),
            },

            {'column': 'oid',
            'column_title': _(u'column_oid', default=u'OID'),
            },

            {'column': 'document',
            'column_title': _(u'column_document', default=u'Document'),
            'transform': linked_document
            },

            {'column': 'status',
            'column_title': _(u'column_status', default=u'Status'),
            },

            {'column': 'result',
            'column_title': _(u'column_result', default=u'Result'),
            },

            {'column': 'policy',
            'column_title': _(u'column_policy', default=u'Policy'),
            },

        )

    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        queue_name = self.request.get('queue')
        context = self.context
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        setSite(portal)
        conn = portal._p_jar
        root = conn.root()
        queues = root[zc.async.interfaces.KEY]
        queue = queues.get(queue_name)

        query = []
        for i, job in enumerate(queue):
            context_path = job.args[0]
            #portal_path = job.args[1]
            #users_path = job.args[2]
            #user_name = job.args[3]
            #func = job.args[4]
            #arguments = job.args[5]
            policy = str(job.getRetryPolicy().__class__).replace("<class '", '').replace("'>", '')
            oid = u64(job._p_oid)
            query.append({'position': i,
                          'oid': oid,
                          'document': context_path,
                          'status': job.status,
                          'result': job.result,
                          'policy': policy
                          })
        return query

