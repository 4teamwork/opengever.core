from plone.restapi.services import Service
from plone.restapi.services.types.get import check_security
from plone.restapi.types.utils import get_jsonschema_for_portal_type
from zope.annotation import IAnnotations
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


TYPE_TO_BE_ADDED_KEY = 'plone.restapi.portal_type_to_be_added'


@implementer(IPublishTraverse)
class GEVERSchemaGet(Service):
    """Endpoint that serializes intent-aware schemas.
    """

    def __init__(self, context, request):
        super(GEVERSchemaGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if len(self.params) == 0:
            # Edit intent
            self.intent = 'edit'
            portal_type = self.context.portal_type

        elif len(self.params) == 1:
            # Add intent
            self.intent = 'add'
            portal_type = self.params[0]
            request_annotations = IAnnotations(self.request)
            request_annotations[TYPE_TO_BE_ADDED_KEY] = portal_type

        else:
            return self._error(
                400, "Bad Request",
                "Must supply either zero or one (portal_type) parameters"
            )

        check_security(self.context)
        self.content_type = "application/json+schema"
        try:
            return get_jsonschema_for_portal_type(
                portal_type, self.context, self.request
            )
        except KeyError:
            self.content_type = "application/json"
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": 'Type "{}" could not be found.'.format(portal_type),
            }
