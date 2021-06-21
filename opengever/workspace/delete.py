from Acquisition import aq_parent
from opengever.document.document import IBaseDocument
from opengever.trash.trash import ITrasher
from opengever.workspace.interfaces import IDeleter
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IToDoList
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.interfaces import IWorkspaceMeetingAgendaItem
from opengever.workspace.utils import is_within_workspace_root
from plone import api
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from zExceptions import Forbidden
from zope.component import adapter
from zope.component import queryAdapter
from zope.interface import implementer


@implementer(IDeleter)
class BaseWorkspaceContenteDeleter(object):
    """Deleter adapter used for deleting objects over the REST-API
    """

    permission = "Delete objects"

    def __init__(self, context):
        self.context = context

    def delete(self):
        self.verify_may_delete()
        self._delete()

    def _delete(self):
        parent = aq_parent(self.context)
        try:
            parent._delObject(self.context.getId())
        except LinkIntegrityNotificationException:
            pass

    def verify_may_delete(self, main=True):
        if main:
            self.check_within_workspace()
        self.check_delete_permission()

    def check_within_workspace(self):
        if not is_within_workspace_root(self.context):
            raise Forbidden()

    def check_delete_permission(self):
        if not api.user.has_permission(self.permission, obj=self.context):
            raise Forbidden()


@adapter(IToDo)
class TodoDeleter(BaseWorkspaceContenteDeleter):

    permission = 'opengever.workspace: Delete Todos'


@adapter(IToDoList)
class TodoListDeleter(BaseWorkspaceContenteDeleter):

    permission = 'opengever.workspace: Delete Todos'


@adapter(IWorkspaceMeetingAgendaItem)
class WorkspaceMeetingAgendaItemDeleter(BaseWorkspaceContenteDeleter):

    permission = 'opengever.workspace: Delete Workspace Meeting Agenda Items'


@adapter(IBaseDocument)
class WorkspaceDocumentDeleter(BaseWorkspaceContenteDeleter):

    permission = 'opengever.workspace: Delete Documents'

    def verify_may_delete(self, main=True):
        super(WorkspaceDocumentDeleter, self).verify_may_delete()
        if not ITrasher(self.context).is_trashed():
            raise Forbidden


@adapter(IWorkspaceFolder)
class WorkspaceFolderDeleter(BaseWorkspaceContenteDeleter):

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
