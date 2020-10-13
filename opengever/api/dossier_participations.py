from opengever.api.batch import SQLHypermediaBatch
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.contact import is_contact_feature_enabled
from opengever.contact.models import Participation
from opengever.contact.sources import ContactsSource
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
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


def validate_roles(context, roles):
    if not roles:
        raise BadRequest("A list of roles is required")
    available_roles = getVocabularyRegistry().get(context, "opengever.dossier.participation_roles")
    for role in roles:
        if role not in available_roles:
            raise BadRequest("Role '{}' does not exist".format(role))


def get_sql_participant(context, participant_id):
    source = ContactsSource(context)
    try:
        term = source.getTermByToken(participant_id)
    except Exception:
        raise BadRequest("{} is not a valid id".format(participant_id))
    return term.value


def get_plone_actor(participant_id):
    actor = ActorLookup(participant_id).lookup()
    if not isinstance(actor, (ContactActor, InboxActor, OGDSUserActor, PloneUserActor)):
        raise BadRequest("{} is not a valid id".format(participant_id))
    return actor


@implementer(IExpandableElement)
@adapter(IDossierMarker, IOpengeverBaseLayer)
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


class ParticipationsGet(Service):
    """API Endpoint which returns a list of all participations for the current
    dossier.

    GET /@participations HTTP/1.1
    """

    def reply(self):
        participations = Participations(self.context, self.request)
        return participations(expand=True)["participations"]


class ParticipationsPost(Service):
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
        validate_roles(self.context, roles)
        return participant_id, roles

    def add_plone_participation(self, participant_id, roles):
        get_plone_actor(participant_id)
        handler = IParticipationAware(self.context)
        existing_participation = handler.get_participation_by_contact_id(participant_id)
        if existing_participation:
            raise BadRequest("There is already a participation for {}".format(participant_id))

        participation = handler.create_participation(**{"contact": participant_id, "roles": roles})
        handler.append_participiation(participation)

    def add_sql_participation(self, participant_id, roles):
        participant = get_sql_participant(self.context, participant_id)
        query = participant.participation_class.query.by_participant(
            participant).by_dossier(self.context)
        if query.count():
            raise BadRequest("There is already a participation for {}".format(participant_id))
        participant.participation_class.create(
            participant=participant, dossier=self.context, roles=roles)

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        participant_id, roles = self.extract_data()
        if is_contact_feature_enabled():
            self.add_sql_participation(participant_id, roles)
        else:
            self.add_plone_participation(participant_id, roles)

        self.request.response.setStatus(204)
        return None


class ParticipationsPatch(Service):
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
        validate_roles(self.context, roles)
        return roles

    def update_plone_participation(self, participant_id, new_roles):
        get_plone_actor(participant_id)
        handler = IParticipationAware(self.context)
        participation = handler.get_participation_by_contact_id(participant_id)
        if not participation:
            raise BadRequest("{} has no participations on this context".format(participant_id))
        handler.update_participation(participation, new_roles)

    def update_sql_participation(self, participant_id, new_roles):
        participant = get_sql_participant(self.context, participant_id)
        participation = participant.participation_class.query.by_participant(
            participant).by_dossier(self.context).first()
        if not participation:
            raise BadRequest("{} has no participations on this context".format(participant_id))
        participation.update_roles(new_roles)

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


class ParticipationsDelete(Service):
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
        get_plone_actor(participant_id)
        handler = IParticipationAware(self.context)
        participation = handler.get_participation_by_contact_id(participant_id)
        if not participation:
            raise BadRequest("{} has no participations on this context".format(participant_id))
        participation = handler.remove_participation(participation)

    def delete_sql_participation(self, participant_id):
        participant = get_sql_participant(self.context, participant_id)
        participation = participant.participation_class.query.by_participant(
            participant).by_dossier(self.context).first()
        if not participation:
            raise BadRequest("{} has no participations on this context".format(participant_id))
        participation.delete()

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
