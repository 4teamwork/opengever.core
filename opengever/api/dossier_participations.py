from contextlib import contextmanager
from opengever.api.batch import SQLHypermediaBatch
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.contact import is_contact_feature_enabled
from opengever.contact.models import Participation
from opengever.contact.sources import ContactsSource
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.participations import DupplicateParticipation
from opengever.dossier.participations import InvalidParticipantId
from opengever.dossier.participations import InvalidRole
from opengever.dossier.participations import MissingParticipation
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.actor import ContactActor
from opengever.ogds.base.actor import InboxActor
from opengever.ogds.base.actor import OGDSUserActor
from opengever.ogds.base.actor import PloneUserActor
from opengever.ogds.base.sources import UsersContactsInboxesSource
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

    vocabulary = getVocabularyRegistry().get(context, "opengever.dossier.participation_roles")
    return [{"token": term.token, "title": term.title} for term in vocabulary]


def get_plone_actor(participant_id):
    actor = ActorLookup(participant_id).lookup()
    if not isinstance(actor, (ContactActor, InboxActor, OGDSUserActor, PloneUserActor)):
        raise BadRequest("{} is not a valid id".format(participant_id))
    return actor


@implementer(IExpandableElement)
@adapter(IParticipationAwareMarker, IOpengeverBaseLayer)
class Participations(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_sql_participations(self):
        query = Participation.query.by_dossier(self.context)
        batch = SQLHypermediaBatch(self.request, query)
        items = []
        source = ContactsSource(self.context)
        for participation in batch:
            participant_id = source.getTerm(participation.participant).token
            items.append({
                "@id": "{}/@participations/{}".format(self.context.absolute_url(), participant_id),
                "participant_id": participant_id,
                "participant_title": participation.participant.get_title(),
                "roles": [role.role for role in participation.roles]})
        return batch, items

    def get_plone_participations(self):
        handler = IParticipationAware(self.context)
        participations = list(handler.get_participations())

        batch = HypermediaBatch(self.request, participations)
        items = []
        for participation in batch:
            actor = ActorLookup(participation.contact).lookup()
            items.append({
                "@id": '{}/@participations/{}'.format(self.context.absolute_url(),
                                                      participation.contact),
                "participant_id": participation.contact,
                "participant_title": actor.get_label(),
                "roles": list(participation.roles)})
        return batch, items

    def __call__(self, expand=False):
        result = {'participations': {
            '@id': '/'.join((self.context.absolute_url(), '@participations'))}}
        if not expand:
            return result

        if is_contact_feature_enabled():
            batch, items = self.get_sql_participations()
        else:
            batch, items = self.get_plone_participations()

        result["participations"]["available_roles"] = available_roles(self.context)
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

    def update_plone_participation(self, participant_id, new_roles):
        with self.handle_errors():
            self.handler.validate_participant(participant_id)
            self.handler.update_participation(participant_id, new_roles)

    def update_sql_participation(self, participant_id, new_roles):
        with self.handle_errors():
            self.handler.update_participation(participant_id, new_roles)

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        new_roles = self.extract_roles()
        participant_id = self.read_params()
        if is_contact_feature_enabled():
            self.update_sql_participation(participant_id, new_roles)
        else:
            self.update_plone_participation(participant_id, new_roles)

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

    def delete_plone_participation(self, participant_id):
        with self.handle_errors():
            self.handler.validate_participant(participant_id)
            self.handler.remove_participation(participant_id)

    def delete_sql_participation(self, participant_id):
        with self.handle_errors():
            self.handler.remove_participation(participant_id)

    def reply(self):
        participant_id = self.read_params()
        if is_contact_feature_enabled():
            self.delete_sql_participation(participant_id)
        else:
            self.delete_plone_participation(participant_id)

        self.request.response.setStatus(204)
        return None


class PossibleParticipantsGet(Service):
    def reply(self):
        if is_contact_feature_enabled():
            source = ContactsSource(self.context)
        else:
            source = UsersContactsInboxesSource(self.context)
        query = safe_unicode(self.request.form.get('query', ''))
        results = source.search(query)

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
