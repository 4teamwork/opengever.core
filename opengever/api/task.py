from opengever.api.response import ResponsePost
from opengever.api.response import SerializeResponseToJson
from opengever.task.task_response import TaskResponse
from opengever.task.task_response import ITaskResponse
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ITaskResponse, Interface)
class SerializeTaskResponseToJson(SerializeResponseToJson):

    model = ITaskResponse


class TaskResponsePost(ResponsePost):
    """Add a Response to the current context.
    """

    response_class = TaskResponse
