from opengever.tabbedview import _ as tabbedview_mf
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.helper import linked_containing_maindossier


class RepositoryFolderDocuments(Documents):

    disabled_actions = (
        'zip_selected',  # disabled because ZIP does not work on repository folders
        'send_as_email',  # target not available on repository folders
        'trashed',  # target not available on repository folders
    )

    @property
    def enabled_actions(self):
        actions = super(RepositoryFolderDocuments, self).enabled_actions
        return [action for action in actions if action not in self.disabled_actions]

    @property
    def columns(self):
        columns = list(super(RepositoryFolderDocuments, self).columns)
        after_column = filter(lambda col: col['column'] == 'containing_subdossier', columns)[0]
        columns.insert(columns.index(after_column),
                       {'column': 'containing_dossier',
                        'column_title': tabbedview_mf('containing_dossier', 'Dossier'),
                        'transform': linked_containing_maindossier})
        return columns
