from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossiertransfer.model import DossierTransfer
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
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


class FullTransferContentSerializer(object):

    def __init__(self, transfer):
        self.transfer = transfer

    def __call__(self):
        # TODO
        content = {
            'dossiers': DossiersSerializer(self.transfer)(),
            'documents': DocumentsSerializer(self.transfer)(),
            'contacts': [],
        }
        return content


class DossiersSerializer(object):
    """Returns the list of (sub)dossiers included in the transfer.
    """

    ignored_keys = (
        '@components',
        'items',
        'items_total',
        'next_item',
        'previous_item',
    )

    def __init__(self, transfer):
        self.transfer = transfer

    def __call__(self):
        # This currently returns a flat list of dossiers, ordered by path
        # (parents before children, so in the order they should be created).
        # Depending on what is easiest to use on the deserialization side, we
        # might want to change this to return a hierarchical structure.
        serialized_dossiers = []

        catalog = api.portal.get_tool('portal_catalog')

        root_dossier = api.content.uuidToObject(self.transfer.root)
        query = {
            'path': '/'.join(root_dossier.getPhysicalPath()),
            'object_provides': IDossierMarker.__identifier__,
            'sort_on': 'path',
        }
        all_dossiers = catalog.unrestrictedSearchResults(**query)

        for brain in all_dossiers:
            dossier = brain.getObject()
            serialized = getMultiAdapter(
                (dossier, getRequest()), ISerializeToJson)()

            for key in self.ignored_keys:
                serialized.pop(key, None)

            serialized['@id'] = dossier.absolute_url()
            serialized_dossiers.append(serialized)

        return serialized_dossiers


class DocumentsSerializer(object):
    """Returns the list of documents included in the transfer.
    """

    ignored_keys = (
        '@components',
    )

    def __init__(self, transfer):
        self.transfer = transfer

    def __call__(self):
        serialized_documents = []

        catalog = api.portal.get_tool('portal_catalog')

        root_dossier = api.content.uuidToObject(self.transfer.root)

        # Query for all documents by default...
        query = {
            'path': '/'.join(root_dossier.getPhysicalPath()),
            'object_provides': IBaseDocument.__identifier__,
            'sort_on': 'path',
        }

        if not self.transfer.all_documents:
            query['UID'] = self.transfer.documents

        matching_documents = catalog.unrestrictedSearchResults(**query)

        for brain in matching_documents:
            document = brain.getObject()
            serialized = getMultiAdapter(
                (document, getRequest()), ISerializeToJson)()

            for key in self.ignored_keys:
                serialized.pop(key, None)

            serialized['@id'] = document.absolute_url()
            serialized_documents.append(serialized)

        return serialized_documents
