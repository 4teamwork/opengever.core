from collective.elephantvocabulary import wrap_vocabulary
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from ftw.solr.converters import to_iso8601
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.helpers import display_name
from opengever.base.interfaces import ISearchSettings
from opengever.base.solr import OGSolrDocument
from opengever.base.utils import get_preferred_language_code
from opengever.globalindex.browser.report import task_type_helper as task_type_value_helper
from opengever.task.helper import task_type_helper
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.registry.interfaces import IRegistry
from plone.restapi.batching import HypermediaBatch
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.ZCatalog.Lazy import LazyMap
from zExceptions import BadRequest
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
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


def get_path_depth(context):
    # This mirrors the implementation in ftw.solr
    return len(context.getPhysicalPath()) - 1


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
    'is_subdossier': ('is_subdossier', 'is_subdossier', 'is_subdossier'),
    'is_subtask': ('is_subtask', 'is_subtask', 'is_subtask'),
    'issuer_fullname': ('issuer', 'issuer_fullname', 'issuer'),
    'issuer': ('issuer', 'issuer', 'issuer'),
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
    'UID': ('UID', 'UID', 'UID'),
    'firstname': ('firstname', 'firstname', 'firstname'),
    'lastname': ('lastname', 'lastname', 'lastname'),
    'email': ('email', 'email', 'email'),
    'phone_office': ('phone_office', 'phone_office', 'phone_office'),
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

FILTERS = {
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
    ],
    u'todos': [
        u'object_provides:opengever.workspace.interfaces.IToDo',
    ],
    u'proposals': [
        u'object_provides:opengever.meeting.proposal.IProposal',
    ],
    u'contacts': [
        u'object_provides:opengever.contact.contact.IContact',
    ]
}


def translate_document_type(document_type):
    portal = getSite()
    voc = wrap_vocabulary(
            'opengever.document.document_types',
            visible_terms_from_registry='opengever.document.interfaces.'
                                        'IDocumentType.document_types')(portal)
    try:
        term = voc.getTerm(document_type)
    except LookupError:
        return document_type
    else:
        return term.title


def translate_task_type(task_type):
    return task_type_value_helper(task_type)


FACET_TRANSFORMS = {
    'responsible': display_name,
    'review_state': lambda state: translate(state, domain='plone',
                                            context=getRequest()),
    'document_type': translate_document_type,
    'task_type': translate_task_type,
    'checked_out': display_name,
    'Creator': display_name,
}


def with_active_solr_only(func):
    """Raises an error if solr is not activated
    """
    def validate(*args, **kwargs):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        if not settings.use_solr:
            raise BadRequest("Solr is deactivated. The @listing endpoint is "
                             "only available with an activated solr")

        return func(*args, **kwargs)
    return validate


class Listing(Service):
    """List of content items"""

    @with_active_solr_only
    def reply(self):
        name = self.request.form.get('name')
        if name not in FILTERS:
            raise BadRequest

        start = self.request.form.get('b_start', '0')
        rows = self.request.form.get('b_size', '25')
        try:
            start = int(start)
            rows = int(rows)
        except ValueError:
            start = 0
            rows = 25

        sort_on = self.request.form.get('sort_on', DEFAULT_SORT_INDEX)
        sort_on = FIELDS.get(sort_on, (None, None, DEFAULT_SORT_INDEX))[2]
        sort_order = self.request.form.get('sort_order', 'descending')
        sort = sort_on
        if sort:
            if sort_order in ['descending', 'reverse']:
                sort += ' desc'
            else:
                sort += ' asc'

        term = self.request.form.get('search', '').strip()
        query = '*:*'
        if term:
            pattern = (
                u'(Title:{term}* OR SearchableText:{term}*'
                u' OR metadata:{term}*)')
            term_queries = [
                pattern.format(term=escape(safe_unicode(t))) for t in term.split()]
            query = u' AND '.join(term_queries)

        filters = self.request.form.get('filters', {})
        if not isinstance(filters, record):
            filters = {}
        filter_queries = []

        # Exclude searchroot
        context_uid = IUUID(self.context, None)
        if context_uid:
            filter_queries.append(u'-UID:%s' % context_uid)

        if 'trashed' not in filters:
            filter_queries.append(u'trashed:false')
        filter_queries.extend(FILTERS[name])
        filter_queries.append(u'path_parent:{}'.format(escape(
            '/'.join(self.context.getPhysicalPath()))))

        depth = self.request.form.get('depth', -1)
        try:
            depth = int(depth)
        except ValueError:
            depth = -1

        if depth > 0:
            context_depth = get_path_depth(self.context)
            max_path_depth = context_depth + depth
            filter_queries.append(u'path_depth:[* TO {}]'.format(max_path_depth))

        for key, value in filters.items():
            if key not in FIELDS:
                continue
            key = FIELDS[key][0]
            if key is None:
                continue
            if key in DATE_INDEXES:
                # It seems solr needs date filters unescaped, hence we
                # only escape the other filter values
                value = self.daterange_filter(value)
            elif isinstance(value, list):
                value = map(escape, value)
                value = map(safe_unicode, value)
                value = u' OR '.join(value)
            else:
                value = escape(value)
            if value is not None:
                # XXX: Instead of littering all this code with safe_unicode,
                # we should convert user-supplied input to unicode *once*
                # at the system boundaries (when extracting values from
                # self.request.form) once this endpoint gets refactored.
                value = safe_unicode(value)
                filter_queries.append(u'{}:({})'.format(escape(key), value))

        columns = self.request.form.get('columns', [])
        params = {
            'fl': self.field_list(columns),
            'q.op': 'AND',
        }

        facets = self.request.form.get('facets', [])
        facet_fields = filter(None, map(self.field_name_to_index, facets))
        if facet_fields:
            params["facet"] = "true"
            params["facet.mincount"] = 1
            params["facet.field"] = facet_fields

        solr = getUtility(ISolrSearch)
        resp = solr.search(
            query=query, filters=filter_queries, start=start, rows=rows,
            sort=sort, **params)

        # We map the index names back to the field names for the facets
        facet_counts = {}
        for field in facets:
            index_name = self.field_name_to_index(field)
            if index_name is None or index_name not in resp.facets:
                continue
            facet_counts[field] = resp.facets[index_name]

        items = LazyMap(OGSolrDocument,
                        start * [None] + resp.docs,
                        actual_result_count=resp.num_found,)

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

        if facet_counts:
            for field, facets in facet_counts.items():
                transform = FACET_TRANSFORMS.get(FIELDS[field][0])
                for facet, count in facets.items():
                    facets[facet] = {"count": count}
                    if transform:
                        facets[facet]['label'] = transform(facet)
                    else:
                        facets[facet]['label'] = facet
            res['facets'] = facet_counts

        return res

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

    @staticmethod
    def field_name_to_index(field):
        if field in FIELDS:
            return FIELDS[field][0]
        return None

    def field_list(self, columns):
        fl = ['UID', 'getIcon', 'portal_type', 'path', 'id',
              'bumblebee_checksum']
        fl.extend(filter(None, map(self.field_name_to_index, columns)))
        return fl

    def daterange_filter(self, value):
        date_from, date_to = self.parse_dates(value)
        if date_from is not None and date_to is not None:
            return u'[{} TO {}]'.format(
                to_iso8601(date_from), to_iso8601(date_to))
