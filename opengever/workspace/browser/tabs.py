from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import linked
from opengever.tabbedview.helper import readable_date
from opengever.tabbedview.helper import readable_ogds_author
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


class Todos(BaseCatalogListingTab):

    types = ['opengever.workspace.todo']

    columns = (

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked,
         'width': 500},

        {'column': 'responsible',
         'column_title': _(u'label_responsible',
                           default=u"Responsible"),
         'transform': readable_ogds_author},

        {'column': 'deadline',
         'column_title': _(u'label_deadline', default=u'Deadline'),
         'transform': readable_date},
    )
