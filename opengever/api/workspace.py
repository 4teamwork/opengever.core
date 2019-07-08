from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from opengever.workspace.todos.storage import ToDoListStorage
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.content.add import FolderPost
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IWorkspace, Interface)
class SerializeWorkspaceToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceToJson, self).__call__(*args, **kwargs)

        manager = ManageParticipants(self.context, self.request)

        result[u"can_manage_participants"] = manager.can_manage_member()

        return result


class WorkspacePost(FolderPost):

    def reply(self):
        result = super(WorkspacePost, self).reply()
        data = json_body(self.request)

        if result.get('@type') == 'opengever.workspace.todo':
            result = self.handle_add_todo(data, result)

        return result

    def handle_add_todo(self, data, result):
        todo_list_id = data.get('todo_list_id')
        if todo_list_id:
            ToDoListStorage(self.context).add_todo_to_list(todo_list_id,
                                                           result.get('UID'))

        return result
