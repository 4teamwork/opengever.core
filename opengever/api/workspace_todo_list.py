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


class ToDoListDelete(ToDoListTraverseService):
    """API-Endpoint to remove todo-lists or todos from a list.

    DELETE workspace/@todolist/{list-id} HTTP/1.1
    DELETE workspace/@todolist/{list-id}/{todo-id} HTTP/1.1
    """
    def reply(self):
        todo_list_id, todo_uid = self.read_params()

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if todo_uid:
            self.handle_delete_todo_from_list(todo_uid)
        self.handle_delete_todo_list(todo_list_id)

        self.request.response.setStatus(204)
        return None

    def handle_delete_todo_list(self, todo_list_id):
        storage = ToDoListStorage(self.context)

        if todo_list_id not in storage._todo_lists_by_id:
            raise NotFound("The given todo_list_id does not exist")

        if storage._todo_lists_by_id.get(todo_list_id).get('todo_uids'):
            raise BadRequest("Removing a todo_list with assigned todos is not allowed")
        storage.remove_todo_list_by_id(todo_list_id)

    def handle_delete_todo_from_list(self, todo_uid):
        storage = ToDoListStorage(self.context)

        if todo_uid not in storage._todos_by_uid:
            raise NotFound("The given todo_uid does not exist in any list")

        storage.remove_todo_from_current_list(todo_uid)

    def read_params(self):
        if len(self.params) == 2:
            return self.params[0], self.params[1]

        if len(self.params) == 1:
            return self.params[0], None

        raise BadRequest(
            "Must supply list-id or a list-id and a todo-uid as URL path parameters.")


class ToDoListPatch(ToDoListTraverseService):
    """API-Endpoint to update the title of a todo-list.

    PATCH workspace/@todolist/{list-id} HTTP/1.1
    {
        "title": 'New title'
    }
    """
    def reply(self):
        data = json_body(self.request)
        todo_list_id = self.read_params()

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        return json_compatible(self.handle_update_todo_list(todo_list_id, data))

    def handle_update_todo_list(self, todo_list_id, data):
        title = data.get('title')

        if not title:
            raise BadRequest("The request body requires the 'title' attribute.")

        storage = ToDoListStorage(self.context)
        if todo_list_id not in storage._todo_lists_by_id:
            raise NotFound("The given todo_list_id does not exist")

        return storage.rename_todo_list(todo_list_id, title)

    def read_params(self):
        if len(self.params) == 1:
            return self.params[0]

        raise BadRequest(
            "Must supply list-id as URL path parameters.")
