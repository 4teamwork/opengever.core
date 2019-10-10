from opengever.api.response import ResponsePost
from opengever.api.response import SerializeResponseToJson
from opengever.task.interfaces import ICommentResponseHandler
from opengever.task.task_response import ITaskResponse
from plone.restapi.interfaces import ISerializeToJson
from zExceptions import Unauthorized
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

    def create_response(self, text):
        response_handler = ICommentResponseHandler(self.context)
        if not response_handler.is_allowed():
            raise Unauthorized(
                "The current user is not allowed to add comments")

        return response_handler.add_response(text)
