from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.dossiertransfer.model import DossierTransfer
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(DossierTransfer, IOpengeverBaseLayer)
class SerializeDossierTransferToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    content_type = 'virtual.ogds.dossiertransfer'

    def __call__(self):
        transfer = self.context
        result = json_compatible({
            'id': transfer.id,
            'title': transfer.title,
            'message': transfer.message,
            'created': transfer.created,
            'expires': transfer.expires,
            'state': transfer.state,
            'source': {
                'token': transfer.source.unit_id,
                'title': transfer.source.title,
            },
            'target': {
                'token': transfer.target.unit_id,
                'title': transfer.target.title,
            },
            'source_user': transfer.source_user_id,
            'root': transfer.root,
            'documents': transfer.documents,
            'participations': transfer.participations,
            'all_documents': transfer.all_documents,
            'all_participations': transfer.all_participations,
        })

        url = '/'.join((
            api.portal.get().absolute_url(),
            '@dossier-transfers/%s' % transfer.id,
        ))
        result.update({'@id': url})
        result.update({'@type': self.content_type})
        return result
