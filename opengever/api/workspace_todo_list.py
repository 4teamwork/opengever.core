from opengever.workspace.todos.storage import ToDoListStorage
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class ToDoListTraverseService(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ToDoListTraverseService, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@participations as parameters
        self.params.append(name)
        return self


class ToDoListPost(ToDoListTraverseService):
    """Adds a todo-list or a todo to a list

    POST workspace/@todolist HTTP/1.1
    {
        "title": "01 - General"
    }

    POST workspace/@todolist/{list-id} HTTP/1.1
    {
        "uid": "xxx"
    }
    """

    def reply(self):
        data = json_body(self.request)
        todo_list_id = self.read_params()

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if todo_list_id:
            todo_list = self.handle_add_todo_to_list(todo_list_id, data)
        else:
            todo_list = self.handle_create_todo_list(data)

        return todo_list.serialize(self.context)

    def handle_create_todo_list(self, data):
        title = data.get('title')

        if not title:
            raise BadRequest("The request body requires the 'title' attribute.")

        storage = ToDoListStorage(self.context)
        return storage.create_todo_list(title)

    def handle_add_todo_to_list(self, todo_list_id, data):
        todo_uid = data.get('todo_uid')

        if not todo_uid:
            raise BadRequest("The request body requires the 'todo_uid' attribute.")

        storage = ToDoListStorage(self.context)

        if todo_list_id not in storage._todo_lists_by_id:
            raise NotFound("The given todo_list_id does not exist")

        return storage.add_todo_to_list(todo_list_id, todo_uid)

    def read_params(self):
        if len(self.params) == 1:
            return self.params[0]
        return None
