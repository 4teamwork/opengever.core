from ftw.dictstorage.interfaces import IDictStorage
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from opengever.api.listing import FILTERS
from opengever.base import _
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.solr import batched_solr_results
from opengever.base.solr import OGSolrDocument
from opengever.base.solr.fields import DateListingField
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zope.component import getUtility
from zope.component import queryMultiAdapter
import json


class BaseReporterView(BrowserView):
    """Base class for XLS Reporting views, which provide the functionality
    to use the users grid settings (visible columns, column order).
    """

    @property
    def _columns(self):
        """Returns a list of dicts of all available excel columns.
        """
        raise NotImplementedError

    def columns(self):
        return self.filter_and_order_by_tabbedview_settings(self._columns)

    def filter_and_order_by_tabbedview_settings(self, excel_columns):
        active_columns = []
        tabbedview_columns = self.get_active_tabbedview_columns()
        if not tabbedview_columns:
            return excel_columns

        for col in tabbedview_columns:
            column = self.excel_column_by_tabbedview_name(excel_columns, col.get('id'))
            if column:
                active_columns.append(column)

        return active_columns

    def excel_column_by_tabbedview_name(self, excel_columns, tv_col_name):
        """Get the Excel column matching the given TabbedView column name.

        For Catalog based Excel exports, the Excel column's sort_index is
        identical to the TabbedView column name.
        """
        excel_columns_by_name = {
            col.get('sort_index', col.get('id')): col
            for col in excel_columns
        }
        return excel_columns_by_name.get(tv_col_name)

    def get_grid_state(self, view_name):
        """Load tabbedview gridstate of the logged in users for the given view.
        """
        tabbedview = self.context.restrictedTraverse(
            "@@tabbedview_view-{}".format(view_name), default=None)
        if not tabbedview:
            return None

        generator = queryMultiAdapter((self.context, tabbedview, self.request),
                                      IGridStateStorageKeyGenerator)
        key = generator.get_key()
        storage = IDictStorage(tabbedview)
        state = storage.get(key)

        if not state:
            return {}

        return json.loads(state)

    def get_active_tabbedview_columns(self):
        """Loads corresponding tabbedview grid-state and returns an orderd
        list of the current visible columns.
        """
        view_name = self.request.form.get('view_name', None)
        grid_state = self.get_grid_state(view_name)
        if grid_state:
            return [col for col in
                    grid_state.get('columns') if not col.get('hidden')]

    def return_excel(self, reporter):
        data = reporter()
        if not data:
            msg = _(u'Could not generate the report.')
            api.portal.show_message(msg, request=self.request, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE
        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        set_attachment_content_disposition(self.request, self.filename)

        return data


class SolrReporterView(BaseReporterView):

    batch_size = 1000
    field_mapper = None

    def __init__(self, *args, **kwargs):
        super(SolrReporterView, self).__init__(*args, **kwargs)
        self.solr = getUtility(ISolrSearch)
        self.fields = self.field_mapper(self.solr)

    def get_selected_items(self):
        paths = self.request.get('paths')
        include_children = self.request.get('include_children', False)
        listing_name = self.request.get('listing_name')
        if not paths and not listing_name:
            return

        if paths and listing_name:
            raise BadRequest('You can query either by paths or by a listing.')

        fields = [col['id'] for col in self.columns()]

        solr_query = {}
        solr_query['rows'] = self.batch_size
        solr_query['fl'] = self.fields.get_query_fields(fields) + ['path']

        if paths:
            self._extend_selected_items_query_by_paths(solr_query, paths, include_children=include_children)
        elif listing_name:
            self._extend_selected_items_query_by_listing(solr_query, listing_name)

        for batch in batched_solr_results(**solr_query):
            for doc in batch:
                doc = OGSolrDocument(doc, fields=self.solr.manager.schema.fields)
                yield IContentListingObject(doc)

    def _extend_selected_items_query_by_paths(self, solr_query, paths, include_children=False):
        filter_queries = []
        # Try to fetch the current sort
        try:
            listing = queryMultiAdapter((self.context, self.request), name="GET_application_json_@listing")
            listing.listing_name = self.corresponding_listing_name
            query, filters, start, rows, sort, field_list, params = listing.prepare_solr_query(self.request.form)
        except KeyError:
            sort = 'modified desc'

        filter_queries.extend(FILTERS.get(listing.listing_name, []))

        if include_children:
            sort = 'path asc'

        solr_query["sort"] = sort

        path_filters = []
        path_filters.append('path:({})'.format(' OR '.join([escape(path) for path in paths])))

        if include_children:
            path_filters.append('path_parent:({})'.format(' OR '.join([escape(path) for path in paths])))
        filter_queries.append('({})'.format(' OR '.join(path_filters)))

        solr_query['fq'] = filter_queries

    def _extend_selected_items_query_by_listing(self, solr_query, listing_name):
        listing = queryMultiAdapter((self.context, self.request), name="GET_application_json_@listing")
        listing.listing_name = listing_name
        query, filters, start, rows, sort, field_list, params = listing.prepare_solr_query(self.request.form)

        solr_query['sort'] = sort
        solr_query['query'] = query
        solr_query['filters'] = filters

    @property
    def is_frontend_request(self):
        return 'columns' in self.request

    def columns(self):
        if self.is_frontend_request:
            return self.filter_and_order_by_request_columns(self._columns)
        else:
            return self.filter_and_order_by_tabbedview_settings(self._columns)

    def filter_and_order_by_request_columns(self, excel_columns):
        requested_columns = self.get_requested_column_names()
        return sorted(
            excel_columns,
            key=lambda col: requested_columns.index(col['id'])
        )

    @property
    def _columns(self):
        requested_cols = self.get_requested_column_names()

        columns = []
        for requested_col in requested_cols:
            # Dynamically create a column definition based on field mapper
            field = self.fields.get(requested_col, only_allowed=True)
            if not field:
                continue

            column = {
                'id': field.field_name,
                'accessor': field.accessor,
                'sort_index': field.sort_index,
                'title': field.get_title(),
            }

            if isinstance(field, DateListingField):
                column['number_format'] = DATE_NUMBER_FORMAT

            # Update it with overrides from explicit column settings
            column_settings = self.get_column_settings(requested_col)
            column.update(column_settings)

            columns.append(column)

        return columns

    def get_requested_column_names(self):
        column_names = self.request.get('columns', self.get_default_column_names())
        return map(self.canonical_name, column_names)

    def get_default_column_names(self):
        return [c['id'] for c in self.column_settings if c.get('is_default')]

    @property
    def column_settings_by_id(self):
        return {c['id']: c for c in self.column_settings}

    @property
    def column_aliases(self):
        return dict(
            zip(
                [c.get('alias', c['id']) for c in self.column_settings],
                [c['id'] for c in self.column_settings]
            )
        )

    def canonical_name(self, column_name):
        return self.column_aliases.get(column_name, column_name)

    def get_column_settings(self, column_name):
        return self.column_settings_by_id.get(column_name, {})

    def excel_column_by_tabbedview_name(self, excel_columns, tv_col_name):
        """Get the Excel column matching the given TabbedView column name.

        For Solr based Excel exports, the corresponding sort_index in Solr
        usually matches the TabbedView column name. Exceptions from this rule
        can be controlled using 'tabbedview_column' in the column settings.
        """
        excel_columns_by_id = {col['id']: col for col in excel_columns}
        tabbedview_columns = {
            c.get('tabbedview_column', c['sort_index']): c['id']
            for c in self._columns
        }
        col_id = tabbedview_columns.get(tv_col_name, tv_col_name)
        return excel_columns_by_id.get(col_id)
