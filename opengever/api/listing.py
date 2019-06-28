from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from ftw.solr.converters import to_iso8601
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import ISearchSettings
from opengever.base.solr import OGSolrDocument
from opengever.base.utils import get_preferred_language_code
from opengever.task.helper import task_type_helper
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.registry.interfaces import IRegistry
from plone.restapi.batching import HypermediaBatch
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.Lazy import LazyMap
from Products.ZCTextIndex.ParseTree import ParseError
from zope.component import getUtility
from ZPublisher.HTTPRequest import record
import Missing


DEFAULT_SORT_INDEX = 'modified'


def create_list_item(item, fields):
    obj = IContentListingObject(item)
    data = {'@id': obj.getURL()}
    for field in fields:
        if field not in FIELDS:
            continue
        accessor = FIELDS[field][1]
        if isinstance(accessor, str):
            value = getattr(obj, accessor, None)
            if callable(value):
                value = value()
        else:
            value = accessor(obj)
        data[field] = json_compatible(value)
    return data


def translated_title(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        attr = 'title_{}'.format(get_preferred_language_code())
        return getattr(obj, attr, obj.Title())
    else:
        return obj.Title()


def translated_task_type(obj):
    return task_type_helper(obj, obj.task_type)


def filesize(obj):
    try:
        filesize = obj.filesize
        if filesize != Missing.Value:
            return filesize
    except AttributeError:
        pass
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return 0
    if info.value is None:
        return 0
    return info.value.size


def filename(obj):
    try:
        filename = obj.filename
        if filename != Missing.Value:
            return filename
    except AttributeError:
        pass
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return None
    if info.value is None:
        return None
    return info.value.filename


def relative_path(brain):
    portal_path_length = len(api.portal.get().getPhysicalPath())
    content_path = brain.getPath().split('/')
    return '/'.join(content_path[portal_path_length:])


# Mapping of field name -> (index, accessor, sort index)
FIELDS = {
    'bumblebee_checksum': (None, 'bumblebee_checksum', DEFAULT_SORT_INDEX),
    'changed': ('changed', 'changed', 'changed'),
    'checked_out': ('checked_out', 'checked_out', 'checked_out'),
    'checked_out_fullname': ('checked_out', 'checked_out_fullname', 'checked_out'),
    'completed': ('completed', 'completed', 'completed'),
    'containing_dossier': ('containing_dossier', 'containing_dossier', 'containing_dossier'),
    'containing_subdossier': ('containing_subdossier', 'containing_subdossier', 'containing_subdossier'),  # noqa
    'created': ('created', 'created', 'created'),
    'creator': ('Creator', 'Creator', 'Creator'),
    'deadline': ('deadline', 'deadline', 'deadline'),
    'delivery_date': ('delivery_date', 'delivery_date', 'delivery_date'),
    'description': ('Description', 'Description', 'Description'),
    'document_author': ('document_author', 'document_author', 'document_author'),
    'document_date': ('document_date', 'document_date', 'document_date'),
    'document_type': ('document_type', 'document_type', 'document_type'),
    'end': ('end', 'end', 'end'),
    'file_extension': ('file_extension', 'file_extension', 'file_extension'),
    'filename': ('filename', filename, 'filename'),
    'filesize': ('filesize', filesize, 'filesize'),
    'has_sametype_children': ('has_sametype_children', 'has_sametype_children',
                              'has_sametype_children'),
    'issuer_fullname': ('issuer', 'issuer_fullname', 'issuer'),
    'keywords': ('Subject', 'Subject', 'Subject'),
    'mimetype': ('getContentType', 'getContentType', 'mimetype'),
    'modified': ('modified', 'modified', 'modified'),
    'pdf_url': (None, 'preview_pdf_url', DEFAULT_SORT_INDEX),
    'preview_url': (None, 'get_preview_frame_url', DEFAULT_SORT_INDEX),
    'receipt_date': ('receipt_date', 'receipt_date', 'receipt_date'),
    'reference': ('reference', 'reference', 'reference'),
    'reference_number': ('reference', 'reference', 'reference'),
    'relative_path': (None, relative_path, DEFAULT_SORT_INDEX),
    'responsible': ('responsible', 'responsible', 'responsible'),
    'responsible_fullname': ('responsible', 'responsible_fullname', 'responsible'),
    'review_state': ('review_state', 'review_state', 'review_state'),
    'review_state_label': ('review_state', 'translated_review_state',
                           'review_state'),
    'sequence_number': ('sequence_number', 'sequence_number', 'sequence_number'),
    'start': ('start', 'start', 'start'),
    'task_type': ('task_type', translated_task_type, 'task_type'),
    'thumbnail_url': (None, 'preview_image_url', DEFAULT_SORT_INDEX),
    'title': ('Title', translated_title, 'sortable_title'),
    'type': ('portal_type', 'PortalType', 'portal_type'),
    '@type': ('portal_type', 'PortalType', 'portal_type'),
}

DATE_INDEXES = set([
    'changed',
    'created',
    'delivery_date',
    'document_date',
    'end',
    'modified',
    'receipt_date',
    'start',
    'deadline',
])

SOLR_FILTERS = {
    u'dossiers': [
        u'object_provides:opengever.dossier.behaviors.dossier.IDossierMarker',
    ],
    u'documents': [
        u'object_provides:opengever.document.behaviors.IBaseDocument',
    ],
    u'workspaces': [
        u'object_provides:opengever.workspace.interfaces.IWorkspace',
    ],
    u'workspace_folders': [
        u'object_provides:opengever.workspace.interfaces.IWorkspaceFolder',
    ],
    u'tasks': [
        u'object_provides:opengever.task.task.ITask',
    ]
}

CATALOG_QUERIES = {
    'dossiers': {
        'object_provides': 'opengever.dossier.behaviors.dossier.IDossierMarker',  # noqa
    },
    'documents': {
        'object_provides': 'opengever.document.behaviors.IBaseDocument',
    },
    'workspaces': {
        'object_provides': 'opengever.workspace.interfaces.IWorkspace',
    },
    'workspace_folders': {
        'object_provides': 'opengever.workspace.interfaces.IWorkspaceFolder',
    },
    'tasks': {
        'object_provides': 'opengever.task.task.ITask',
    }

}


class Listing(Service):
    """List of content items"""

    def reply(self):
        name = self.request.form.get('name')

        start = self.request.form.get('b_start', '0')
        rows = self.request.form.get('b_size', '25')
        try:
            start = int(start)
            rows = int(rows)
        except ValueError:
            start = 0
            rows = 25

        sort_on = self.request.form.get('sort_on', DEFAULT_SORT_INDEX)
        sort_on = FIELDS.get(sort_on, (None, DEFAULT_SORT_INDEX))[2]
        sort_order = self.request.form.get('sort_order', 'descending')
        term = self.request.form.get('search', '').strip()
        columns = self.request.form.get('columns', [])
        filters = self.request.form.get('filters', {})
        if not isinstance(filters, record):
            filters = {}

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        if settings.use_solr:
            items = self.solr_results(
                name, term, columns, start, rows, sort_on, sort_order, filters)
        else:
            items = self.catalog_results(
                name, term, start, rows, sort_on, sort_order, filters)

        batch = HypermediaBatch(self.request, items)
        res = {}
        res['@id'] = batch.canonical_url
        res['items_total'] = batch.items_total
        res['b_start'] = start
        res['b_size'] = rows
        if batch.links:
            res['batching'] = batch.links

        res['items'] = []
        for item in items[start:start + rows]:
            res['items'].append(create_list_item(item, columns))

        return res

    def catalog_results(self, name, term, start, rows, sort_on, sort_order,
                        filters):
        if name not in CATALOG_QUERIES:
            return []

        query = CATALOG_QUERIES[name].copy()
        query.update({
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': -1,
                'exclude_root': 1,
            },
            'sort_on': sort_on,
            'sort_order': sort_order,
            'sort_limit': start + rows,
        })

        if term:
            query['SearchableText'] = term + '*'

        for key, value in filters.items():
            if key not in FIELDS:
                continue
            key = FIELDS[key][0]
            if key is None:
                continue
            if key in DATE_INDEXES:
                value = self.catalog_daterange_query(value)
            query[key] = value

        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            return catalog(**query)
        except ParseError:
            return []

    def parse_dates(self, value):
        if isinstance(value, list):
            value = value[0]
        if not isinstance(value, str):
            return None, None

        dates = value.split('TO')
        if len(dates) == 2:
            try:
                date_from = DateTime(dates[0]).earliestTime()
                date_to = DateTime(dates[1]).latestTime()
            except DateTimeError:
                return None, None
        return date_from, date_to

    def catalog_daterange_query(self, value):
        date_from, date_to = self.parse_dates(value)
        if date_from is not None and date_to is not None:
            return {'query': [date_from, date_to], 'range': 'minmax'}

    def solr_results(self, name, term, columns, start, rows, sort_on,
                     sort_order, filters):

        if name not in SOLR_FILTERS:
            return []

        query = '*:*'
        if term:
            pattern = (
                u'(Title:{term}* OR SearchableText:{term}*'
                u' OR metadata:{term}*)')
            term_queries = [
                pattern.format(term=escape(t)) for t in term.split()]
            query = u' AND '.join(term_queries)

        filter_queries = []
        if 'trashed' not in filters:
            filter_queries.append(u'trashed:false')
        filter_queries.extend(SOLR_FILTERS[name])
        filter_queries.append(u'path_parent:{}'.format(escape(
            '/'.join(self.context.getPhysicalPath()))))

        for key, value in filters.items():
            if key not in FIELDS:
                continue
            key = FIELDS[key][0]
            if key is None:
                continue
            if key in DATE_INDEXES:
                value = self.solr_daterange_filter(value)
            elif isinstance(value, list):
                value = u' OR '.join(value)
            if value is not None:
                filter_queries.append(u'{}:({})'.format(key, value))

        sort = sort_on
        if sort:
            if sort_order in ['descending', 'reverse']:
                sort += ' desc'
            else:
                sort += ' asc'

        params = {
            'fl': self.solr_field_list(columns),
            'q.op': 'AND',
        }

        solr = getUtility(ISolrSearch)
        resp = solr.search(
            query=query, filters=filter_queries, start=start, rows=rows,
            sort=sort, **params)
        return LazyMap(
            OGSolrDocument,
            start * [None] + resp.docs,
            actual_result_count=resp.num_found,
        )

    def solr_field_list(self, columns):
        fl = ['UID', 'getIcon', 'portal_type', 'path', 'id',
              'bumblebee_checksum']
        for col in columns:
            if col in FIELDS:
                field = FIELDS[col][0]
                if field is not None:
                    fl.append(field)
        return fl

    def solr_daterange_filter(self, value):
        date_from, date_to = self.parse_dates(value)
        if date_from is not None and date_to is not None:
            return u'[{} TO {}]'.format(
                to_iso8601(date_from), to_iso8601(date_to))
