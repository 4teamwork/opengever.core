from collections import defaultdict
from opengever.activity import notification_center
from opengever.activity.roles import ROLE_TRANSLATIONS
from opengever.activity.roles import WATCHER_ROLE
from opengever.activity.sources import PossibleWatchersSource
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.api.schema.querysources import RawQuerySourceSearchResults
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.actor import OGDSUserActor
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IExpandableElement)
class Watchers(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.center = notification_center()

    def __call__(self, expand=False):
        result = {
            'watchers': {
                '@id': '/'.join((self.context.absolute_url(), '@watchers')),
            },
        }
        if not expand:
            return result

        roles = set()
        watchers_and_roles = defaultdict(list)
        for subscription in self.center.get_subscriptions(self.context):
            actor = ActorLookup(subscription.watcher.actorid).lookup()
            if actor.is_active:
                watchers_and_roles[subscription.watcher.actorid].append(subscription.role)
                roles.add(subscription.role)

        referenced_actors = []
        for actor_id in watchers_and_roles:
            referenced_actors.append(serialize_actor_id_to_json_summary(actor_id))

        referenced_watcher_roles = [
            {
                'id': role,
                'title': translate(ROLE_TRANSLATIONS[role], context=self.request)
            }
            for role in roles]

        result['watchers']['watchers_and_roles'] = watchers_and_roles
        result['watchers']['referenced_watcher_roles'] = referenced_watcher_roles
        result['watchers']['referenced_actors'] = referenced_actors
        return result


class WatchersGet(Service):

    def reply(self):
        watchers = Watchers(self.context, self.request)
        return watchers(expand=True)['watchers']


class WatchersPost(Service):

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        self.extract_data()
        self.center = notification_center()
        self.center.add_watcher_to_resource(self.context, self.actor_id, WATCHER_ROLE)
        self.request.response.setStatus(204)
        return super(WatchersPost, self).reply()

    def extract_data(self):
        data = json_body(self.request)
        self.actor_id = data.get("actor_id", None)
        if not self.actor_id:
            raise BadRequest("Property 'actor_id' is required")
        try:
            PossibleWatchersSource(self.context).getTermByToken(self.actor_id)
        except LookupError:
            raise BadRequest(u"Actor '{}' does not exist".format(self.actor_id))


@implementer(IPublishTraverse)
class WatchersDelete(Service):
    def __init__(self, context, request):
        super(WatchersDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@watchers as parameters
        self.params.append(name)
        return self

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        self.extract_data()
        actor_id = self.read_params()
        if not self.can_delete_actor(actor_id):
            raise Forbidden()

        self.center = notification_center()
        self.center.remove_watcher_from_resource(self.context, actor_id, WATCHER_ROLE)

        self.request.response.setStatus(204)
        return None

    def extract_data(self):
        data = json_body(self.request)
        if data:
            raise BadRequest("DELETE does not take any data")

    def can_delete_actor(self, actor_id):
        # The user can always remove itslef
        if actor_id == api.user.get_current().getId():
            return True

        # The user can never remove another user
        if isinstance(ActorLookup(actor_id).lookup(), OGDSUserActor):
            return False

        # the user can remove groups and teams
        return True

    def read_params(self):
        if len(self.params) == 0:
            raise BadRequest("Must supply an actor ID as URL path parameter.")

        if len(self.params) > 1:
            raise BadRequest("Only actor ID is supported URL path parameter.")

        return self.params[0]


class PossibleWatchers(Service):
    def reply(self):
        source = PossibleWatchersSource(self.context)
        query = safe_unicode(self.request.form.get('query', ''))
        result = RawQuerySourceSearchResults(source, source.raw_search(query))

        batch = HypermediaBatch(self.request, result.results)

        serialized_terms = []
        for term in batch:
            serializer = getMultiAdapter(
                (result.get_resolved_term(term), self.request), interface=ISerializeToJson
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
