from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm.query import Query
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from zope.interface import implements, Interface
from ftw.table import helper
from five import grok
from opengever.tabbedview import _
from sqlalchemy import or_
from ftw.tabbedview.browser.listing import ListingView
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.ogds.base.model.user import User
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.helper import email_helper
from opengever.tabbedview.helper import boolean_helper
from zope.component import getUtility



def linked_value_helper(item, value):
    """Helper for linking the value with the user profile.
    """

    info = getUtility(IContactInformation)
    url = info.get_profile_url(getattr(item, 'userid', None))

    if url:
        return '<a href="%s">%s</a>' % (url, value)
    else:
        return value


class IUsersListingTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configuration using the OGDS users
    model as source.
    """


class UsersListing(grok.CodeView, OpengeverTab, ListingView):
    """Tab registered on contacts folder (see opengever.contact) listing all
    users.
    """

    implements(IUsersListingTableSourceConfig)

    grok.name('tabbedview_view-users')
    grok.context(Interface)

    sort_on = 'lastname'
    sort_order = ''

    show_selects = False
    enabled_actions = []
    major_actions = []

    columns = (
        {'column': 'lastname',
         'column_title': _(u'label_userstab_lastname',
                           default=u'Lastname'),
         'transform': linked_value_helper},

        {'column': 'firstname',
         'column_title': _(u'label_userstab_firstname',
                           default=u'Firstname'),
         'transform': linked_value_helper},

        {'column': 'userid',
         'column_title': _(u'label_userstab_userid',
                           default=u'Userid'),
         'transform': linked_value_helper},

        {'column': 'email',
         'column_title': _(u'label_userstab_email',
                           default=u'Email'),
         'transform': email_helper},

        {'column': 'phone_office',
         'column_title': _(u'label_userstab_phone_office',
                           default=u'Office Phone')},

        {'column': 'active',
         'column_title': _(u'label_active',
                           default=u'Active'),
         'transform': boolean_helper},

        )

    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        info = getUtility(IContactInformation)
        return info._users_query()


class UsersListingTableSource(grok.MultiAdapter, BaseTableSource):
    """Table source OGDS users.
    """

    grok.implements(ITableSource)
    grok.adapts(IUsersListingTableSourceConfig, Interface)


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

            model = User

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

                query = query.filter(or_(*[field.like(term)
                                           for field in fields]))

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
