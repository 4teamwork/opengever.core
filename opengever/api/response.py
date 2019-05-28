from opengever.task.adapters import IResponse
from opengever.task.response import ITaskTransitionResponseFormSchema
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
class SerializeTaskResponseToJson(SerializeFolderToJson):

    # The `reminder_option` is not stored on the response object, but the
    # field only controls the reminder of the task.
    SKIPPED_FIELDS = ['reminder_option']

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kwargs):
        result = {
            'date': json_compatible(self.context.date),
            'creator': json_compatible(self.context.creator),
            'added_object': json_compatible(self.context.added_object),
            'changes': json_compatible(self.context.changes),
        }

        # Add attributes from the response schema
        for name, field in getFields(ITaskTransitionResponseFormSchema).items():
            if name in self.SKIPPED_FIELDS:
                continue

            serializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldSerializer)
            value = serializer()
            result[json_compatible(name)] = value

        return result
