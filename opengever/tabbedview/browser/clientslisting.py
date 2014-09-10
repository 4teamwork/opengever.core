from five import grok
from ftw.table import helper
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import create_session
from opengever.ogds.models.org_unit import OrgUnit
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import OpengeverTab
from opengever.tabbedview.browser.listing import ListingView
from sqlalchemy import or_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import asc, desc
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import implements
from zope.interface import Interface


def linked_url_helper(item, value):
    """Creates a link to `value`, if it's url-ish.
    """
    if '://' in value:
        return '<a href="%s">%s</a>' % (value, value)
    else:
        return value


def readable_inbox_group(item, value):
    return item.inbox_group.groupid


def readable_user_group(item, value):
    return item.users_group.groupid


class IClientsTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using the
    OGDS clients as source.
    """


class ClientsListing(grok.View, OpengeverTab, ListingView):
    """A clients listing tab.
    """

    implements(IClientsTableSourceConfig)

    grok.context(Interface)
    grok.name('tabbedview_view-ogds-cp-clients')
    grok.require('cmf.ManagePortal')

    sort_on = 'client_id'
    sort_reverse = False

    show_selects = False
    enabled_actions = []
    major_actions = []
    selection = ViewPageTemplateFile("no_selection_amount.pt")

    columns = (

        {'column': 'client_id',
         'column_title': _(u'column_client_id', default=u'Client ID')},

        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title')},

        {'column': 'enabled',
         'column_title': _(u'column_enabled', default=u'Enabled')},

        {'column': 'ip_address',
         'column_title': _(u'column_ip_address', default=u'IP address')},

        {'column': 'site_url',
         'column_title': _(u'column_interal_site_url',
                           default=u'Internal site URL')},

        {'column': 'public_url',
         'column_title': _(u'column_public_url', default=u'Public URL'),
         'transform': linked_url_helper},

        {'column': 'group',
         'column_title': _(u'column_group', default=u'Users group'),
         'transform': readable_user_group},

        {'column': 'inbox_group',
         'column_title': _(u'column_inbox_group', default=u'Inbox user group'),
         'transform': readable_inbox_group},

        )

    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        return create_session().query(OrgUnit)


class ClientsTableSource(grok.MultiAdapter, BaseTableSource):
    """Clients source adapter.
    """

    grok.implements(ITableSource)
    grok.adapts(IClientsTableSourceConfig, Interface)

    def validate_base_query(self, query):
        """Validates and fixes the base query. Returns the query object.
        It may raise e.g. a `ValueError` when something's wrong.
        """

        if not isinstance(query, Query):
            raise ValueError('Expected query to be a sqlalchemy query '
                             'object.')

        return query

    def extend_query_with_ordering(self, query):
        """Extends the given `query` with ordering information and returns
        the new query.
        """

        if self.config.sort_on:
            order_f = self.config.sort_reverse and desc or asc

            query = query.order_by(order_f(self.config.sort_on))

        return query

    def extend_query_with_textfilter(self, query, text):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """

        if len(text):
            # remove trailing asterisk
            if text.endswith('*'):
                text = text[:-1]

            model = Task

            # first lets lookup what fields (= sql columns) we have
            fields = []
            for column in self.config.columns:
                try:
                    colname = column['column']
                except TypeError:
                    # its not dict
                    continue

                # do not support dates
                if column.get('transform') == helper.readable_date:
                    continue

                field = getattr(model, colname, None)
                if field:
                    fields.append(field)

            # lets split up the search term into words, extend them with
            # the default wildcards and then search for every word
            # seperately
            for word in text.strip().split(' '):
                term = '%%%s%%' % word

                query = query.filter(or_(*[f.like(term) for f in fields]))

        return query

    def extend_query_with_batching(self, query):
        """Extends the given `query` with batching filters and returns the
        new query. This method is only called when batching is enabled in
        the source config with the `batching_enabled` attribute.
        """

        if not self.config.batching_enabled:
            # batching is disabled
            return query

        if not self.config.lazy:
            # do not batch since we are not lazy
            return query

        # we need to know how many records we would have without batching
        self.full_length = query.count()

        # now add batching
        pagesize = self.config.batching_pagesize
        current_page = self.config.batching_current_page
        start = pagesize * (current_page - 1)

        query = query.offset(start)
        query = query.limit(pagesize)

        return query

    def search_results(self, query):
        """Executes the query and returns a tuple of `results`.
        """

        self.full_length = query.count()

        # not lazy
        if not self.config.lazy or not self.config.batching_enabled:
            return query.all()

        page_results = query.all()

        pagesize = self.config.batching_pagesize
        current_page = self.config.batching_current_page
        start = pagesize * (current_page - 1)

        results = list(xrange(start)) + \
            page_results + \
            list(xrange(self.full_length - start - len(page_results)))

        return results
