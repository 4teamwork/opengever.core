from datetime import datetime
from opengever.api import _
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.base.response import COMMENT_REMOVED_RESPONSE_TYPE
from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.base.response import IResponse
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.ogds.base.actor import Actor
from persistent.dict import PersistentDict
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.schema import getFields
from zope.schema.interfaces import IField


@adapter(IField, IResponse, Interface)
@implementer(IFieldSerializer)
class ResponseDefaultFieldSerializer(object):

    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        return json_compatible(self.get_value())

    def get_value(self, default=None):
        return getattr(self.context, self.field.__name__, default)


@implementer(ISerializeToJson)
@adapter(IResponse, Interface)
class SerializeResponseToJson(SerializeFolderToJson):

    model = IResponse

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kwargs):
        response_url = '{}/@responses/{}'.format(
            kwargs['container'].absolute_url(), self.context.response_id)

        result = {'@id': response_url}
        for name, field in getFields(self.model).items():
            serializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldSerializer)
            value = serializer()
            result[json_compatible(name)] = value

        # Provide token and title for the creator
        result['creator'] = {
            'token': self.context.creator,
            'title': Actor.lookup(self.context.creator).get_label(with_principal=False)
        }
        return result


@implementer(IPublishTraverse)
class ResponseGet(Service):
    """Representation of a single response.
    """

    def __init__(self, context, request):
        super(ResponseGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@responses as parameters
        self.params.append(name)
        return self

    @property
    def _get_response_id(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (the response id)")
        return self.params[0]

    def reply(self):
        response_container = IResponseContainer(self.context)
        if self._get_response_id not in response_container:
            raise NotFound

        response = response_container[self._get_response_id]
        serializer = getMultiAdapter((response, self.request), ISerializeToJson)

        return serializer(container=self.context)


class ResponsePost(Service):
    """Add a Response to the current context.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)

        text = data.get('text')

        if not text:
            raise BadRequest("Property 'text' is required")

        response = self.create_response(text)

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", self.context.absolute_url())

        serializer = getMultiAdapter((response, self.request), ISerializeToJson)
        return serializer(container=self.context)

    def create_response(self, text):
        response = Response(COMMENT_RESPONSE_TYPE)
        response.text = text
        IResponseContainer(self.context).add(response)
        return response


@implementer(IPublishTraverse)
class ResponsePatch(Service):
    """Edit a response.
    """

    def __init__(self, context, request):
        super(ResponsePatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@responses as parameters
        self.params.append(name)
        return self

    @property
    def _get_response_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (response id)")
        return self.params[0]

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        response_container = IResponseContainer(self.context)
        if self._get_response_id not in response_container:
            raise NotFound

        response = response_container[self._get_response_id]
        if response.response_type != COMMENT_RESPONSE_TYPE:
            raise NotReportedBadRequest(
                _(u'only_comment_type_can_be_edited',
                  default=u'Only responses of type "Comment" can be edited.'))

        data = json_body(self.request)
        text = data.get('text')

        if not text:
            raise BadRequest("Property 'text' is required")

        response.text = text
        response.modified = datetime.now()
        response.modifier = api.user.get_current().id

        self.request.response.setStatus(204)
        self.request.response.setHeader("Location", self.context.absolute_url())


@implementer(IPublishTraverse)
class ResponseDelete(Service):
    """Delete a response.
    """

    response_class = Response

    def __init__(self, context, request):
        super(ResponseDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@responses as parameters
        self.params.append(name)
        return self

    @property
    def _get_response_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (response id)")
        return self.params[0]

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        response_container = IResponseContainer(self.context)
        if self._get_response_id not in response_container:
            raise NotFound

        response = response_container[self._get_response_id]
        if response.response_type != COMMENT_RESPONSE_TYPE:
            raise NotReportedBadRequest(
                _(u'only_comment_type_can_be_deleted',
                  default=u'Only responses of type "Comment" can be deleted.'))

        self.create_response(response)
        response_container.delete(response.response_id)
        return self.reply_no_content()

    def create_response(self, deleted_response):
        response = self.response_class(COMMENT_REMOVED_RESPONSE_TYPE)

        response.additional_data = PersistentDict({
            'deleted_response_creation_date': deleted_response.created
        })
        IResponseContainer(self.context).add(response)
        return response
