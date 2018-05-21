from plone import api
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.ZCTextIndex.ParseTree import ParseError


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

        query['sort_on'] = self.request.form.get('sort_on', 'modified')
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

        headers = self.request.form.get('headers')
        res = {'items': []}
        for item in items[start:start + rows]:
            data = {}
            for header in headers:
                data[header] = json_compatible(getattr(item, header))
            data['@id'] = item.getURL()
            res['items'].append(data)

        res['total'] = len(items)
        res['start'] = start
        res['rows'] = rows

        return res
