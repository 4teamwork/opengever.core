from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.task.adapters import IResponseContainer
from opengever.task.task import ITask
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ITask, Interface)
class SerializeTaskToJson(GeverSerializeFolderToJson):
    def __call__(self, *args, **kwargs):
        result = super(SerializeTaskToJson, self).__call__(*args, **kwargs)

        responses = IResponseContainer(self.context)
        result['responses'] = [
            getMultiAdapter((response, self.request), ISerializeToJson)()
            for response in responses]

        return result
