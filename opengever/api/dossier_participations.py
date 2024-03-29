from contextlib import contextmanager
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.interfaces import IDossierParticipants
from opengever.dossier.participations import DupplicateParticipation
from opengever.dossier.participations import InvalidParticipantId
from opengever.dossier.participations import InvalidRole
from opengever.dossier.participations import IParticipationData
from opengever.dossier.participations import MissingParticipation
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.vocabulary import getVocabularyRegistry


def available_roles(context):
    active_roles = api.portal.get_registry_record('roles', IDossierParticipants) or []
    vocabulary = getVocabularyRegistry().get(context, "opengever.dossier.participation_roles")
    return [{
        "token": term.token,
        "title": term.title,
        "active": term.token in active_roles if active_roles else True
    } for term in vocabulary]


def primary_participation_roles(context):
    primary_roles = api.portal.get_registry_record('primary_participation_roles',
                                                   interface=IDossierParticipants)
    vocabulary = getVocabularyRegistry().get(context, "opengever.dossier.participation_roles")
    roles = []
    for role in primary_roles:
        try:
            term = vocabulary.getTermByToken(role)
            roles.append({"token": term.token, "title": term.title})
        except LookupError:
            continue
    return roles


@implementer(IExpandableElement)
@adapter(IParticipationAwareMarker, IOpengeverBaseLayer)
class Participations(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {'participations': {
            '@id': '/'.join((self.context.absolute_url(), '@participations'))}}
        if not expand:
            return result

        handler = IParticipationAware(self.context)
        participation_data = [IParticipationData(participation)
                              for participation in handler.get_participations()]
        participation_data = sorted(participation_data, key=lambda data: data.participant_title)

        batch = HypermediaBatch(self.request, participation_data)

        items = []
        for data in batch:
            items.append({
                "@id": '{}/@participations/{}'.format(
                    self.context.absolute_url(), data.participant_id),
                "participant_id": data.participant_id,
                "participant_title": data.participant_title,
                "participant_actor": serialize_actor_id_to_json_summary(
                    data.participant_id),
                "roles": data.roles})

        result["participations"]["available_roles"] = available_roles(self.context)
        result["participations"]["primary_participation_roles"] = primary_participation_roles(self.context)
        result["participations"]["items"] = items
        result["participations"]["items_total"] = batch.items_total
        if batch.links:
            result["participations"]["batching"] = batch.links
        return result


class ParticipationBaseService(Service):

    def __init__(self, context, request):
        super(ParticipationBaseService, self).__init__(context, request)
        self.handler = IParticipationAware(self.context)

    @contextmanager
    def handle_errors(self):
        try:
            yield
        except (InvalidParticipantId,
                DupplicateParticipation,
                MissingParticipation,
                InvalidRole) as exc:
            raise BadRequest(exc.message)


class ParticipationsGet(Service):
    """API Endpoint which returns a list of all participations for the current
    dossier.

    GET /@participations HTTP/1.1
    """

    def reply(self):
        participations = Participations(self.context, self.request)
        return participations(expand=True)["participations"]


class ParticipationsPost(ParticipationBaseService):
    """API Endpoint to update an existing participation.

    POST /@participations HTTP/1.1
    {
        "participant_id": "peter.mueller",
        "roles": ["regard", "final-drawing"]
    }
    """

    def extract_data(self):
        data = json_body(self.request)
        participant_id = data.get("participant_id", None)
        roles = data.get("roles", None)
        if not participant_id:
            raise BadRequest("Property 'participant_id' is required")
        return participant_id, roles

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        participant_id, roles = self.extract_data()
        with self.handle_errors():
            self.handler.add_participation(participant_id, roles)

        self.request.response.setStatus(204)
        return None


class ParticipationsPatch(ParticipationBaseService):
    """API Endpoint to update an existing participation.

    PATCH /@participations/peter.mueller HTTP/1.1
    {
        "roles": ["regard", "final-drawing"]
    }
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ParticipationsPatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@participations as parameters
        self.params.append(name)
        return self

    def read_params(self):
        """Returns principal_id, passed in via traversal parameters.
        """
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply participant as URL path parameter.")
        return self.params[0]

    def extract_roles(self):
        data = json_body(self.request)
        roles = data.get("roles", None)
        return roles

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        new_roles = self.extract_roles()
        participant_id = self.read_params()
        with self.handle_errors():
            self.handler.update_participation(participant_id, new_roles)

        self.request.response.setStatus(204)
        return None


class ParticipationsDelete(ParticipationBaseService):
    """API Endpoint to update an existing participation.

    DELETE /@participations/peter.mueller HTTP/1.1
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ParticipationsDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@participations as parameters
        self.params.append(name)
        return self

    def read_params(self):
        """Returns principal_id, passed in via traversal parameters.
        """
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply participant as URL path parameter.")
        return self.params[0]

    def reply(self):
        participant_id = self.read_params()
        with self.handle_errors():
            self.handler.remove_participation(participant_id)

        self.request.response.setStatus(204)
        return None


class PossibleParticipantsGet(Service):
    def reply(self):
        query = safe_unicode(self.request.form.get('query', ''))

        handler = IParticipationAware(self.context)
        results = handler.participant_source.search(query)

        # filter out current participants
        current_participants = set(
            IParticipationData(participation).participant_id
            for participation in handler.get_participations())
        results = [term for term in results if term.token not in current_participants]

        batch = HypermediaBatch(self.request, results)

        serialized_terms = []
        for term in batch:
            serializer = getMultiAdapter(
                (term, self.request), interface=ISerializeToJson
            )
            serialized_terms.append(serializer())

        result = {
            "@id": batch.canonical_url,
            "items": serialized_terms,
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            result["batching"] = links
        return result
