from five import grok
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource
from opengever.tabbedview.filtered_source import FilteredTableSourceMixin
from opengever.tabbedview.interfaces import IGeverTableSourceConfig
from sqlalchemy import or_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import desc
from zope.interface import Interface


class SqlTableSource(grok.MultiAdapter, FilteredTableSourceMixin, BaseTableSource):
    """Base table source adapter for every listing,
       that gets the content from sql.
    """

    searchable_columns = []

    grok.implements(ITableSource)
    grok.adapts(IGeverTableSourceConfig, Interface)

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
            sort_on = self.config.sort_on
            # Don't plug column names as literal strings into an order_by
            # clause, but use a ColumnClause instead to allow SQLAlchemy to
            # properly quote the identifier name depending on the dialect
            if isinstance(sort_on, basestring):
                sort_on = column(sort_on)

            order_f = self.config.sort_reverse and desc or asc

            query = query.order_by(order_f(sort_on))

        return query

    def extend_query_with_textfilter(self, query, text):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """

        if len(text):
            if isinstance(text, str):
                text = text.decode('utf-8')

            # remove trailing asterisk
            if text.endswith('*'):
                text = text[:-1]

            # lets split up the search term into words, extend them with
            # the default wildcards and then search for every word
            # seperately
            for word in text.strip().split(' '):
                term = '%%%s%%' % word

                # XXX check if the following hack is still necessary

                # Fixed Problems with the collation with the Oracle DB
                # the case insensitive worked just every second time
                # now it works fine
                # Issue #759
                query.session

                query = query.filter(
                    or_(*[field.like(term) for field in self.searchable_columns]))

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
        # just return executed query everthing else is done
        return query.all()
