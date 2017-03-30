from opengever.task.activities import TaskCommentedActivity
from opengever.task.adapters import IResponseContainer
from opengever.task.adapters import Response
from opengever.task.interfaces import ICommentResponseHandler
from plone import api
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent


class CommentResponseHandler(object):
    implements(ICommentResponseHandler)

    TRANSITION_TYPE = "task-commented"

    def __init__(self, context):
        self.context = context

    def is_allowed(self):
        return api.user.has_permission(
            'opengever.task: Add task comment', obj=self.context)

    def add_response(self, text):
        response = self._create_response(text)
        self._add_response_to_obj(self.context, response)
        self._record_activity(response)

        return self

    def _create_response(self, text):
        response = Response(text)
        response.transition = self.TRANSITION_TYPE

        return response

    def _add_response_to_obj(self, obj, response):
        container = IResponseContainer(obj)
        container.add(response)

        notify(ObjectModifiedEvent(obj))

    def _record_activity(self, response):
        TaskCommentedActivity(self.context,
                              self.context.REQUEST,
                              response).record()
