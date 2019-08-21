from opengever.base.response import IResponse
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.base.response import ResponseContainer
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.services import Service
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
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

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kwargs):
        response_url = '{}/@responses/{}'.format(
            kwargs['container'].absolute_url(), kwargs['response_id'])

        result = {'@id': response_url}
        for name, field in getFields(IResponse).items():
            serializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldSerializer)
            value = serializer()
            result[json_compatible(name)] = value

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
        return serializer(
            container=self.context, response_id=self._get_response_id)


class ResponsePost(Service):
    """Add a Response to the current context.
    """

    def reply(self):
        data = json_body(self.request)

        text = data.get('text')
        IResponse['text'].validate(text)
        response = Response(text)
        response_id = ResponseContainer(self.context).add(response)

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", self.context.absolute_url())

        serializer = getMultiAdapter((response, self.request), ISerializeToJson)
        return serializer(container=self.context, response_id=response_id)
