from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.todolist import IToDoListSchema
from zope.component import adapter


@adapter(IWorkspace)
class WorkspaceSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All workspaces should use the same range/key of sequence numbers.
    """

    key = 'WorkspaceSequenceNumberGenerator'


@adapter(IWorkspaceFolder)
class WorkspaceFolderSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All workspace folders should use the same range/key of sequence numbers.
    """

    key = 'WorkspaceFolderSequenceNumberGenerator'


@adapter(IToDoListSchema)
class TodoListSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """Sequence Number generator for todolist, which uses a global counter.
    """

    key = 'ToDoListSequenceNumberGenerator'


@adapter(IToDo)
class TodoSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """Sequence Number generator for ToDo, which uses a global counter.
    """

    key = 'ToDoSequenceNumberGenerator'
