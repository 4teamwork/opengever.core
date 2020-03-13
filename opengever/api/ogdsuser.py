from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class OGDSUserGet(Service):
    """API Endpoint that returns a single user from ogds.

    GET /@ogds-user/user.id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(OGDSUserGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid = self.read_params()
        return {
            '@id': '{}/@ogds-user/{}'.format(
                self.context.absolute_url(), userid),
            '@type': 'virtual.ogds.user',
        }

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply user ID as URL path parameter.")

        return self.params[0]
