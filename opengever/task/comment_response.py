from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.base.response import IResponseContainer
from opengever.task.activities import TaskCommentedActivity
from opengever.task.interfaces import ICommentResponseHandler
from opengever.task.response_syncer import sync_task_response
from opengever.task.task_response import TaskResponse
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
        self._sync_response(text)

        return self

    def _create_response(self, text):
        response = TaskResponse(COMMENT_RESPONSE_TYPE)
        response.text = text
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

    def _sync_response(self, text):
        sync_task_response(self.context, self.context.REQUEST, 'comment',
                           self.TRANSITION_TYPE, text)
