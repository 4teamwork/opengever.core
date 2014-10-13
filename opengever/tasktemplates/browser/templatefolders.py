from ftw.table import helper
from opengever.tabbedview.helper import linked, translated_string
from opengever.tabbedview.browser.tabs import OpengeverCatalogListingTab
from five import grok
from opengever.tasktemplates import _


class TaskTemplateFoldersTab(OpengeverCatalogListingTab):
    """Tab for listing all task template folders on the template dossier.
    """

    grok.name('tabbedview_view-tasktemplatefolders')

    columns = (

        {'column': '',
         'column_title': '',
         'transform': helper.draggable,
         'sortable': False,
         'width': 30},

        {'column': '',
         'column_title': '',
         'transform': helper.path_checkbox,
         'sortable': False,
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

    enabled_actions = []

    major_actions = []
