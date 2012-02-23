from five import grok
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from ftw.table import helper
from sqlalchemy import or_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import asc, desc
from zope.interface import Interface


class SqlTableSource(grok.MultiAdapter, BaseTableSource):
    """Base table source adapter for every listing,
       that gets the content from sql.
    """

    grok.implements(ITableSource)
    grok.adapts(ITableSourceConfig, Interface)

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
            if isinstance(text, str):
                text = text.decode('utf-8')

            # remove trailing asterisk
            if text.endswith('*'):
                text = text[:-1]

            # get the sqlalchemy model from config, used for a dynamic
            # implementation of the textfiltering functionality
            model = self.config.model

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

                # Fixed Problems with the collation with the Oracle DB
                # the case insensitive worked just every second time
                # now it works fine
                # Issue #759
                query.session

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
        #just return executed query everthing else is done
        return query.all()
