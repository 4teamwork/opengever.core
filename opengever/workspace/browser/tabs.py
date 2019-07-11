from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import linked
from opengever.workspace import _


class Workspaces(BaseCatalogListingTab):

    types = ['opengever.workspace.workspace']

    columns = (

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked,
         'width': 500},

        {'column': 'Description',
         'column_title': _(u'label_description',
                           default=u"Description"),
         'width': 400}
    )


class WorkspaceFolders(Workspaces):
    """List all workspace-folders recursively.
    """

    types = ['opengever.workspace.folder']
