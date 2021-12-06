from copy import deepcopy
from opengever.api.utils import create_proxy_request_error_handler
from opengever.api.utils import default_http_error_code_mapping
from opengever.kub.client import KuBClient
from plone.restapi.services import Service
from zExceptions import BadRequest
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
        client = KuBClient()
        return client.get_full_entity_by_id(_id)

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply ID as URL path parameter.")

        return self.params[0]
