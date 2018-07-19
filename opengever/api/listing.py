from opengever.base.helpers import display_name
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.ZCTextIndex.ParseTree import ParseError
from zope.i18n import translate


QUERIES = {
    'dossiers': {
        'object_provides': 'opengever.dossier.behaviors.dossier.IDossierMarker',
    },
    'documents': {
        'object_provides': 'opengever.document.behaviors.IBaseDocument',
    }
}


class Listing(Service):
    """List of content items"""

    def reply(self):
        name = self.request.form.get('name')
        if name not in QUERIES:
            return {}

        query = QUERIES[name].copy()
        query['path'] = '/'.join(self.context.getPhysicalPath())
        # Exclude context from results, which also matches the path query.
        # Unfortunately UUIDIndex does not support 'not' queries.
        # getId should be unique enough for our use-case, though.
        query['getId'] = {'not': self.context.getId()}

        start = self.request.form.get('start', '0')
        rows = self.request.form.get('rows', '25')
        try:
            start = int(start)
            rows = int(rows)
        except ValueError:
            start = 0
            rows = 25

        sort_on = self.request.form.get('sort_on', DEFAULT_SORT_INDEX)
        query['sort_on'] = COLUMNS.get(sort_on, (None, DEFAULT_SORT_INDEX))[1]
        query['sort_order'] = self.request.form.get('sort_order', 'descending')

        searchable_text = self.request.form.get('search', '').strip()
        if searchable_text:
            query['SearchableText'] = searchable_text + '*'

        try:
            items = api.content.find(**query)
        except ParseError:
            items = []

        if not items:
            return {}

        columns = self.request.form.get('columns', [])
        res = {'items': []}
        for item in items[start:start + rows]:
            obj = IContentListingObject(item)
            data = {}
            for column in columns:
                if column not in COLUMNS:
                    continue
                accessor = COLUMNS[column][0]
                if isinstance(accessor, str):
                    value = getattr(obj, accessor, None)
                    if callable(value):
                        value = value()
                else:
                    value = accessor(obj)
                data[column] = json_compatible(value)

            data['@id'] = item.getURL()
            res['items'].append(data)

        res['total'] = len(items)
        res['start'] = start
        res['rows'] = rows

        return res


def responsible_name(obj):
    return display_name(obj.responsible)


def checked_out(obj):
    return display_name(obj.checked_out)


def translated_review_state(obj):
    return translate(obj.review_state(), domain='plone', context=obj.request)


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


DEFAULT_SORT_INDEX = 'modified'
COLUMNS = {
    'checked_out': (checked_out, 'checked_out'),
    'containing_dossier': ('containing_dossier', 'containing_dossier'),
    'containing_subdossier': ('containing_subdossier', 'containing_subdossier'),
    'created': ('created', 'created'),
    'creator': ('Creator', 'Creator'),
    'delivery_date': ('delivery_date', 'delivery_date'),
    'document_author': ('document_author', 'document_author'),
    'document_date': ('document_date', 'document_date'),
    'end': ('end', 'end'),
    'mimetype': ('getContentType', 'mimetype'),
    'modified': ('modified', 'modified'),
    'receipt_date': ('receipt_date', 'receipt_date'),
    'reference': ('reference', 'reference'),
    'responsible': (responsible_name, 'responsible'),
    'review_state': (translated_review_state, 'review_state'),
    'sequence_number': ('sequence_number', 'sequence_number'),
    'start': ('start', 'start'),
    'thumbnail': ('get_preview_image_url', DEFAULT_SORT_INDEX),
    'title': ('Title', 'sortable_title'),
    'type': ('PortalType', 'portal_type'),
    'filesize': (filesize, 'filesize'),
    'filename': (filename, 'filename'),
}
