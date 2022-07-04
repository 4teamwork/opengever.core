from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.kub.entity import KuBEntity
from opengever.kub.interfaces import IKuBSettings
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


@implementer(ISerializeToJson)
@adapter(KuBEntity, IOpengeverBaseLayer)
class SerializeKuBEntityToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, full_representation=False):
        serialization = self.context.serialize()
        serialization['additional_ui_attributes'] = api.portal.get_registry_record(
            'additional_ui_attributes', interface=IKuBSettings)
        return serialization


class KuBGet(Service):
    """API Endpoint that returns a single user from ogds.

    GET /@kub/contact_uid HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(KuBGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        _id = self.read_params().decode('utf-8')
        try:
            entity = KuBEntity(_id)
            serializer = queryMultiAdapter((entity, self.request), ISerializeToJson)
        except LookupError:
            raise NotFound
        return serializer()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply ID as URL path parameter.")

        return self.params[0]
