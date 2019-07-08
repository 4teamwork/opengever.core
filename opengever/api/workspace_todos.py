from opengever.workspace.interfaces import IToDo
from opengever.workspace.todos.storage import ToDoListStorage
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class ToDoLimitException(Exception):
    """There is no batching for the todos-endpoint.

    For a good working experience it is mandatory that we show all todos at once.

    There will be a naturally limited amount of todos per workspace due to the
    fact, that a workspace is made for a project.

    Anyway, to be prepared for the case that some workspace will have an
    unexpected amount of todos, there is a hard-limit raising an exception if
    reached. In that case, we should thing about an advanced batching
    implementation for todos.
    """


class ToDosGet(Service):
    """API Endpoint which returns a list of all todos for the current
    workspace.

    This endpiont includes the current todo-list configuration.

    GET workspace/@todos HTTP/1.1
    """
    HARD_LIMIT = 5000  # See ToDoLimitException for more information

    def reply(self):
        result = {}
        self.extend_with_todos(result)
        self.extend_with_todo_lists(result)

        return json_compatible(result)

    def extend_with_todos(self, result):
        todos = self.context.listFolderContents(
            contentFilter={'portal_type': 'opengever.workspace.todo'})

        if len(todos) > self.HARD_LIMIT:
            raise ToDoLimitException(
                "This workspace reached the limit of {} todos.".format(
                    self.HARD_LIMIT))

        result['items'] = [
            getMultiAdapter((todo, self.request), ISerializeToJsonSummary)()
            for todo in todos]

    def extend_with_todo_lists(self, result):
        result['todo_lists'] = ToDoListStorage(self.context).list()
