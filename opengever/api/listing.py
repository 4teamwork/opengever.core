from plone import api
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service


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

        query = QUERIES[name]
        query['path'] = '/'.join(self.context.getPhysicalPath())

        items = api.content.find(**query)
        if not items:
            return {}

        headers = self.request.form.get('headers')
        res = {'items': []}
        for item in items[:50]:
            data = {}
            for header in headers:
                data[header] = json_compatible(getattr(item, header))
            data['@id'] = item.getURL()
            res['items'].append(data)

        return res
