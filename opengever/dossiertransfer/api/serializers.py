from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.participations import IParticipationData
from opengever.dossiertransfer.model import DossierTransfer
from opengever.kub.entity import KuBEntity
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
        content = {
            'dossiers': DossiersSerializer(self.transfer)(),
            'documents': DocumentsSerializer(self.transfer)(),
            'contacts': ContactsSerializer(self.transfer)(),
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

        # We only add participations for the root dossier
        if serialized_dossiers[0]['UID'] != self.transfer.root:
            raise RuntimeError(
                'Unexpected first dossier, expected it to match root dossier')

        serialized_dossiers[0]['participations'] = ParticipationsSerializer(self.transfer)()

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


class ContactsSerializer(object):
    """Returns a dictionary of contacts included in the transfer (by KuB ID).
    """

    def __init__(self, transfer):
        self.transfer = transfer

    def __call__(self):
        serialized_contacts = {}
        pcp_serializer = ParticipationsSerializer(self.transfer)

        for kub_entity_id, roles in pcp_serializer():
            serialized = pcp_serializer.serialize_kub_entity_by_id(kub_entity_id)
            serialized_contacts[kub_entity_id] = serialized

        return serialized_contacts


class ParticipationsSerializer(object):
    """Returns a list of (kub_entity_id, roles) tuples for matching participations.

    Matching participations are filtered according to the
    transfer.all_participations flag, and if it is False, the contents of the
    selection list in transfer.participations.

    Participations that contain a KuB 'membership' entity will be resolved to
    the 'person' entity that is referenced by that membership, and the
    respective participant_id key will also be transformed to reflect the
    referenced person's KuB ID.
    """

    def __init__(self, transfer):
        self.transfer = transfer

        self.selection = []
        if self.transfer.participations:
            self.selection = self.transfer.participations

    def __call__(self):
        root_dossier = api.content.uuidToObject(self.transfer.root)
        handler = IParticipationAware(root_dossier)

        participations = [
            IParticipationData(pcp) for pcp in handler.get_participations()
        ]

        matching = []
        for participation in participations:
            if self.include(participation.participant_id):
                key, roles = self.resolve(participation)
                matching.append((key, roles))

        return matching

    def include(self, participant_id):
        if self.transfer.all_participations:
            return True
        return participant_id in self.selection

    def resolve(self, participation):
        kub_entity_id = participation.participant_id
        key = kub_entity_id

        if kub_entity_id.startswith('membership:'):
            # If the participation is a membership, we resolve the referenced
            # person and serialize that, since we don't support the transfer
            # of KuB organizations or memberships
            serialized = self.serialize_kub_entity_by_id(kub_entity_id)
            person_id = 'person:%s' % serialized['person']['id']
            serialized = self.serialize_kub_entity_by_id(person_id)
            key = person_id

        return key, participation.roles

    def serialize_kub_entity_by_id(self, kub_id):
        entity = KuBEntity(kub_id)
        return getMultiAdapter((entity, getRequest()), ISerializeToJson)()
