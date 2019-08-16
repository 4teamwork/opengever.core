from opengever.base.response import IResponse
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
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
        result = {}
        for name, field in getFields(IResponse).items():
            serializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldSerializer)
            value = serializer()
            result[json_compatible(name)] = value

        return result
