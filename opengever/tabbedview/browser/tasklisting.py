from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm.query import Query
from ftw.table.basesource import BaseTableSourceConfig, BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from zope.interface import implements, Interface
from ftw.table import helper
from five import grok
from opengever.base.browser.helper import client_title_helper
from opengever.globalindex.model.task import Task
from opengever.globalindex.utils import indexed_task_link_helper
from opengever.tabbedview import _
from opengever.tabbedview.helper import readable_date_set_invisibles
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import task_id_checkbox_helper
from opengever.task.helper import task_type_helper
from sqlalchemy import or_
from zope.app.pagetemplate import ViewPageTemplateFile


class IGlobalTaskTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using the
    `opengever.globalindex` as source.
    """


class GlobalTaskListingMixin(BaseTableSourceConfig):
    """A tabbed view mixing which brings support for listing tasks from
    the SQL (globally over all clients).

    There is support for searching, batching and ordering.

    Usage:
    Create tab-class subclassing this class and the OpengeverListingTab:

    >>> from opengever.globalindex.interfaces import ITaskQuery
    >>> class MyTaskListing(GlobalTaskListingMixin, OpengeverListingTab):
    ...     grok.name('tabbedview_view-globaltasks')
    ...     grok.require('Permission')
    ...
    ...     def get_base_query(self):
    ...         query_util = getUtility(ITaskQuery)
    ...         return query_util._get_some_tasks_query()
    """

    implements(IGlobalTaskTableSourceConfig)

    sort_on = 'modified'
    sort_reverse = False

    enabled_actions = []
    major_actions = []

    select_all_template = ViewPageTemplateFile('select_all_globaltasks.pt')

    columns = (

        ('', task_id_checkbox_helper),

        {'column': 'review_state',
         'column_title': _(u'column_review_state', default=u'Review state'),
         'transform': helper.translated_string()},

        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': indexed_task_link_helper},

        {'column': 'task_type',
         'column_title': _(u'column_task_type', default=u'Task type'),
         'transform': task_type_helper},

        {'column': 'deadline',
         'column_title': _(u'column_deadline', default=u'Deadline'),
         'transform': helper.readable_date},

        {'column': 'completed',
         'column_title': _(u'column_date_of_completion',
                           default=u'Date of completion'),
         'transform': readable_date_set_invisibles},

        {'column': 'responsible',
         'column_title': _(u'label_responsible_task', default=u'Responsible'),
         'transform': readable_ogds_author},

        {'column': 'issuer',
         'column_title': _(u'label_issuer', default=u'Issuer'),
         'transform': readable_ogds_author},

        {'column': 'created',
         'column_title': _(u'column_issued_at', default=u'Issued at'),
         'transform': helper.readable_date},

        {'column': 'client_id',
         'column_title': _('column_client', default=u'Client'),
         'transform': client_title_helper},

        {'column': 'sequence_number',
         'column_title': _(u'column_sequence_number',
                           default=u'Sequence number')},

        )

    def get_base_query(self):
        """This method must be implement. It has to return a SQLAlchemy
        query object on Task. See the ITaskQuery for further details.
        """
        raise NotImplemented


class GlobalTaskTableSource(grok.MultiAdapter, BaseTableSource):
    """Base table source adapter.
    """

    grok.implements(ITableSource)
    grok.adapts(IGlobalTaskTableSourceConfig, Interface)

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
            for column in self.columns:
                colname = column['column']

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

