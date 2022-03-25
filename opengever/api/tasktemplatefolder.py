from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ITaskTemplateFolderSchema, Interface)
class SerializeTaskTemplateFolderToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeTaskTemplateFolderToJson, self).__call__(*args, **kwargs)
        result['is_subtasktemplatefolder'] = self.context.is_subtasktemplatefolder()
        return result
