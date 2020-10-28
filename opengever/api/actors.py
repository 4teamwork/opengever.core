from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.interfaces import IActor
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


@implementer(ISerializeToJson)
@adapter(IActor, IOpengeverBaseLayer)
class SerializeActorToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        result = {
            '@id': '{}/@actors/{}'.format(
                api.portal.get().absolute_url(), self.context.identifier),
            'actor_type': self.context.actor_type,
            'identifier': self.context.identifier,
            'label': self.context.get_label(with_principal=False),
        }

        return result


class ActorsGet(Service):
    """API Endpoint that returns the data for a single actor.

    GET /@actors/actor-id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ActorsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        actorid = self.read_params()
        actor = ActorLookup(actorid).lookup()
        serializer = queryMultiAdapter((actor, self.request), ISerializeToJson)
        return serializer()

    def read_params(self):
        if len(self.params) == 0:
            raise BadRequest("Must supply an actor ID as URL path parameter.")

        if len(self.params) > 1:
            raise BadRequest("Only actor ID is supported URL path parameter.")

        return self.params[0]
