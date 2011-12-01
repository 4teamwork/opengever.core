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
        ('', helper.draggable),
        ('', helper.path_checkbox),
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
