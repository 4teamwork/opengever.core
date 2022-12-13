from opengever.base.content_deleter import BaseContentDeleter
from opengever.base.interfaces import IDeleter
from opengever.document.document import IBaseDocument
from opengever.trash.trash import ITrasher
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IToDoList
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.interfaces import IWorkspaceMeetingAgendaItem
from opengever.workspace.utils import is_within_workspace_root
from zExceptions import Forbidden
from zope.component import adapter
from zope.component import queryAdapter


class BaseWorkspaceContentDeleter(BaseContentDeleter):
    """Deleter adapter used for deleting workspace objects over the REST-API
    """
    def verify_may_delete(self, main=True):
        if main:
            self.check_within_workspace()
        super(BaseWorkspaceContentDeleter, self).verify_may_delete()

    def check_within_workspace(self):
        if not is_within_workspace_root(self.context):
            raise Forbidden()


@adapter(IToDo)
class TodoDeleter(BaseWorkspaceContentDeleter):

    permission = 'opengever.workspace: Delete Todos'


@adapter(IToDoList)
class TodoListDeleter(BaseWorkspaceContentDeleter):

    permission = 'opengever.workspace: Delete Todos'


@adapter(IWorkspaceMeetingAgendaItem)
class WorkspaceMeetingAgendaItemDeleter(BaseWorkspaceContentDeleter):

    permission = 'opengever.workspace: Delete Workspace Meeting Agenda Items'


@adapter(IBaseDocument)
class WorkspaceDocumentDeleter(BaseWorkspaceContentDeleter):

    permission = 'opengever.workspace: Delete Documents'

    def verify_may_delete(self, main=True):
        super(WorkspaceDocumentDeleter, self).verify_may_delete()
        if not ITrasher(self.context).is_trashed():
            raise Forbidden


@adapter(IWorkspaceFolder)
class WorkspaceFolderDeleter(BaseWorkspaceContentDeleter):

    permission = 'opengever.workspace: Delete Workspace Folders'

    def verify_may_delete(self, main=True):
        super(WorkspaceFolderDeleter, self).verify_may_delete(main=main)
        if not ITrasher(self.context).is_trashed():
            raise Forbidden

        for obj in self.context.objectValues():
            deleter = queryAdapter(obj, IDeleter)
            if deleter is None:
                raise Forbidden()
            deleter.verify_may_delete(main=False)


@adapter(IWorkspace)
class WorkspaceDeleter(BaseWorkspaceContentDeleter):

    permission = 'opengever.workspace: Delete Workspace'

    def verify_may_delete(self, main=True):
        self.check_delete_permission()
        if self.context.external_reference:
            raise Forbidden()
