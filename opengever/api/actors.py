from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.interfaces import IActor
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


def serialize_actor_id_to_json_summary(actor_id):
    """This method is used to return a standardized summary representation
    of an actor. We should keep this very efficient as it will be used by
    various endpoints returning actors or lists of actors for certain fields.
    We therefore should only return data that we can compute without retrieving
    the actual actor object.
    """
    url = '{}/@actors/{}'.format(api.portal.get().absolute_url(), actor_id)
    return {'@id': url,
            'identifier': actor_id}


@implementer(ISerializeToJson)
@adapter(IActor, IOpengeverBaseLayer)
class SerializeActorToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        represents_url = self.context.represents_url()
        represents = {'@id': represents_url} if represents_url else None

        result = {
            '@id': '{}/@actors/{}'.format(
                api.portal.get().absolute_url(), self.context.identifier),
            'active': self.context.is_active,
            'actor_type': self.context.actor_type,
            'identifier': self.context.identifier,
            'label': self.context.get_label(with_principal=False),
            'portrait_url': self.context.get_portrait_url(),
            'representatives': [
                serialize_actor_id_to_json_summary(r.userid)
                for r in self.context.representatives()
            ],
            'represents': represents,
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


class ActorsGetListPOST(Service):
    """This endpoint allows to get the data for a list of actors using
    a POST request containing a list of actor_ids in the request body.

    POST /@actors HTTP/1.1
    """

    @property
    def request_data(self):
        return json_body(self.request)

    def reply(self):
        data = json_body(self.request)
        actor_ids = data.get('actor_ids', [])
        items = []
        for actorid in actor_ids:
            actor = ActorLookup(actorid).lookup()
            serializer = queryMultiAdapter((actor, self.request), ISerializeToJson)
            items.append(serializer())

        result = {}
        result['@id'] = self.request.URL
        result['items'] = items
        return result
