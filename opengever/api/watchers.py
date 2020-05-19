from collections import defaultdict
from opengever.activity import notification_center
from opengever.activity.roles import ROLE_TRANSLATIONS
from opengever.activity.roles import WATCHER_ROLE
from opengever.activity.sources import PossibleWatchersSource
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.ogds.base.actor import ActorLookup
from opengever.task.task import ITask
from plone import api
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(ITask, IOpengeverBaseLayer)
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
            watchers_and_roles[subscription.watcher.actorid].append(subscription.role)
            roles.add(subscription.role)

        portal_url = api.portal.get().absolute_url()
        referenced_users = []
        for actor_id in watchers_and_roles:
            actor = ActorLookup(actor_id).lookup()
            referenced_users.append(
                {
                    '@id': "{}/@users/{}".format(portal_url, actor_id),
                    'id': actor_id,
                    'fullname': actor.get_label(with_principal=False)
                })

        referenced_watcher_roles = [
            {
                'id': role,
                'title': translate(ROLE_TRANSLATIONS[role], context=self.request)
            }
            for role in roles]

        result['watchers']['watchers_and_roles'] = watchers_and_roles
        result['watchers']['referenced_watcher_roles'] = referenced_watcher_roles
        result['watchers']['referenced_users'] = referenced_users
        return result


class WatchersGet(Service):

    def reply(self):
        watchers = Watchers(self.context, self.request)
        return watchers(expand=True)['watchers']


class WatchersPost(Service):

    def reply(self):
        self.extract_data()
        self.center = notification_center()
        self.center.add_watcher_to_resource(self.context, self.userid, WATCHER_ROLE)
        self.request.response.setStatus(204)
        return super(WatchersPost, self).reply()

    def extract_data(self):
        data = json_body(self.request)
        self.userid = data.get("userid", None)
        if not self.userid:
            raise BadRequest("Property 'userid' is required")
        if not api.user.get(self.userid):
            raise BadRequest("userid '{}' does not exist".format(self.userid))


class WatchersDelete(Service):
    def reply(self):
        self.extract_data()
        self.userid = api.user.get_current().getId()
        self.center = notification_center()
        self.center.remove_watcher_from_resource(self.context, self.userid, WATCHER_ROLE)

        self.request.response.setStatus(204)
        return None

    def extract_data(self):
        data = json_body(self.request)
        if data:
            raise BadRequest("DELETE does not take any data")


class PossibleWatchers(Service):
    def reply(self):
        source = PossibleWatchersSource(self.context)
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
