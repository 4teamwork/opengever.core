from opengever.workspace import _
from opengever.tabbedview import GeverTabbedView


class WorkspaceTabbedView(GeverTabbedView):
    """Define the tabs available on a Workspace."""

    folders_tab = {
        'id': 'folders',
        'title': _(u'label_folders', default=u'Folders'),
        }

    documents_tab = {
        'id': 'documents-proxy',
        'title': _(u'label_documents', default=u'Documents'),
        }

    todo_tab = {
        'id': 'todos',
        'title': _(u'label_todo', default=u'ToDo'),
        }

    trash_tab = {
        'id': 'trash',
        'title': _(u'label_trash', default=u'Trash'),
        }

    journal_tab = {
        'id': 'journal',
        'title': _(u'label_journal', default=u'Journal'),
        }

    def _get_tabs(self):
        return filter(None, [
            self.folders_tab,
            self.documents_tab,
            self.todo_tab,
            self.trash_tab,
            self.journal_tab,

        ])


class WorkspaceFolderTabbedView(WorkspaceTabbedView):
    """Define tabs available on Workspace Folder"""


class WorkspaceRootTabbedView(GeverTabbedView):

    workspaces_tab = {
        'id': 'workspaces',
        'title': _(u'label_workspaces', default=u'Workspaces'),
        }

    def _get_tabs(self):
        return filter(None, [
            self.workspaces_tab,
        ])
