from ftw.table import helper
from opengever.tabbedview.helper import linked
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from five import grok


class TaskTemplateFoldersTab(OpengeverListingTab):
    """Tab for listing all task template folders on the template dossier.
    """

    grok.name('tabbedview_view-tasktemplatefolders')

    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('review_state', 'review_state', helper.translated_string()),
        )

    types = ['opengever.tasktemplates.tasktemplatefolder', ]
