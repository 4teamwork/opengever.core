from ftw.table import helper
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import linked
from opengever.tabbedview.helper import translated_string
from opengever.tasktemplates import _


class TaskTemplateFoldersTab(BaseCatalogListingTab):
    """Tab for listing all task template folders on the template folder.
    """

    columns = (

        {'column': '',
         'column_title': '',
         'transform': helper.path_checkbox,
         'sortable': False,
         'groupable': False,
         'width': 30},

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked},
        {'column': 'review_state',
         'column_title': _(u'label_review_state', default=u'Review state'),
         'transform': translated_string()},
    )

    types = ['opengever.tasktemplates.tasktemplatefolder', ]

    search_options = {'is_subtasktemplatefolder': False}

    enabled_actions = ['folder_delete_confirmation']

    major_actions = []
