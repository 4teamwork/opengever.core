from copy import deepcopy
from opengever.api.utils import create_proxy_request_error_handler
from opengever.api.utils import default_http_error_code_mapping
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.kub.entity import KuBEntity
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
import logging

logger = logging.getLogger('opengever.api: KuB')

http_error_code_mapping = deepcopy(default_http_error_code_mapping)
http_error_code_mapping[404] = {
    "return_code": 404,
    "return_message": u"Contact was not found in KuB."}

kub_request_error_handler = create_proxy_request_error_handler(
    logger, u'Error while communicating with KuB', http_error_code_mapping)


@implementer(ISerializeToJson)
@adapter(KuBEntity, IOpengeverBaseLayer)
class SerializeKuBEntityToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, full_representation=False):
        return self.context.serialize()


class KuBGet(Service):
    """API Endpoint that returns a single user from ogds.

    GET /@ogds-users/user.id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(KuBGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    @kub_request_error_handler
    def reply(self):
        _id = self.read_params().decode('utf-8')
        entity = KuBEntity(_id)
        serializer = queryMultiAdapter((entity, self.request), ISerializeToJson)
        return serializer()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply ID as URL path parameter.")

        return self.params[0]
