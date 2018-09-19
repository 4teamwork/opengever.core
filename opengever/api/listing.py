from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import ISearchSettings
from opengever.base.solr import OGSolrDocument
from opengever.base.utils import get_preferred_language_code
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.registry.interfaces import IRegistry
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.ParseTree import ParseError
from zope.component import getUtility


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


def filesize(obj):
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return 0
    if info.value is None:
        return 0
    return info.value.size


def filename(obj):
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return None
    if info.value is None:
        return None
    return info.value.filename


# Mapping of field name -> (index, accessor, sort index)
FIELDS = {
    '@type': ('portal_type', 'PortalType', 'portal_type'),
    'checked_out': ('checked_out', 'checked_out_fullname', 'checked_out'),
    'containing_dossier': ('containing_dossier', 'containing_dossier', 'containing_dossier'),
    'containing_subdossier': ('containing_subdossier', 'containing_subdossier', 'containing_subdossier'),  # noqa
    'created': ('created', 'created', 'created'),
    'creator': ('Creator', 'Creator', 'Creator'),
    'description': ('Description', 'Description', 'Description'),
    'delivery_date': ('delivery_date', 'delivery_date', 'delivery_date'),
    'document_author': ('document_author', 'document_author', 'document_author'),
    'document_date': ('document_date', 'document_date', 'document_date'),
    'end': ('end', 'end', 'end'),
    'mimetype': ('getContentType', 'getContentType', 'mimetype'),
    'modified': ('modified', 'modified', 'modified'),
    'receipt_date': ('receipt_date', 'receipt_date', 'receipt_date'),
    'reference': ('reference', 'reference', 'reference'),
    'reference_number': ('reference', 'reference', 'reference'),
    'responsible': ('responsible', 'responsible_fullname', 'responsible'),
    'review_state': ('review_state', 'translated_review_state', 'review_state'),
    'sequence_number': ('sequence_number', 'sequence_number', 'sequence_number'),
    'start': ('start', 'start', 'start'),
    'thumbnail': (None, 'get_preview_image_url', DEFAULT_SORT_INDEX),
    'title': ('Title', translated_title, 'sortable_title'),
    'type': ('portal_type', 'PortalType', 'portal_type'),
    'filesize': (None, filesize, 'filesize'),
    'filename': (None, filename, 'filename'),
}

SOLR_FILTERS = {
    u'dossiers': [
        u'object_provides:opengever.dossier.behaviors.dossier.IDossierMarker',
    ],
    u'documents': [
        u'object_provides:opengever.document.behaviors.IBaseDocument',
    ]
}

CATALOG_QUERIES = {
    'dossiers': {
        'object_provides': 'opengever.dossier.behaviors.dossier.IDossierMarker',  # noqa
    },
    'documents': {
        'object_provides': 'opengever.document.behaviors.IBaseDocument',
    }
}


class Listing(Service):
    """List of content items"""

    def reply(self):
        name = self.request.form.get('name')

        start = self.request.form.get('start', '0')
        rows = self.request.form.get('rows', '25')
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

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        if settings.use_solr:
            items = self.solr_results(
                name, term, columns, start, rows, sort_on, sort_order)
        else:
            items = self.catalog_results(name, term, rows, sort_on, sort_order)

        if not items:
            return {}

        res = {'items': []}
        for item in items[start:start + rows]:
            res['items'].append(create_list_item(item, columns))
        res['total'] = len(items)
        res['start'] = start
        res['rows'] = rows

        return res

    def catalog_results(self, name, term, rows, sort_on, sort_order):
        if name not in CATALOG_QUERIES:
            return []

        query = CATALOG_QUERIES[name].copy()
        query.update({
            'path': '/'.join(self.context.getPhysicalPath()),
            'sort_on': sort_on,
            'sort_order': sort_order,
            'sort_limit': rows,
        })

        # Exclude context from results, which also matches the path query.
        # Unfortunately UUIDIndex does not support 'not' queries.
        # getId should be unique enough for our use-case, though.
        query['getId'] = {'not': self.context.getId()}

        if term:
            query['SearchableText'] = term + '*'

        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            return catalog(**query)
        except ParseError:
            return []

    def solr_results(self, name, term, columns, start, rows, sort_on,
                     sort_order):

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

        filters = [u'trashed:false']
        filters.extend(SOLR_FILTERS[name])
        filters.append(u'path_parent:{}'.format(escape(
            '/'.join(self.context.getPhysicalPath()))))

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
            query=query, filters=filters, start=start, rows=rows, sort=sort,
            **params)
        return [OGSolrDocument(doc) for doc in resp.docs]

    def solr_field_list(self, columns):
        fl = ['UID', 'getIcon', 'portal_type', 'path', 'id',
              'bumblebee_checksum']
        for col in columns:
            if col in FIELDS:
                field = FIELDS[col][0]
                if field is not None:
                    fl.append(field)
        return fl
