from opengever.tabbedview.browser.tabs import OpengeverListingTab
from ftw.table import helper
from five import grok

class TaskTemplates(OpengeverListingTab):
    grok.name('tabbedview_view-tasktemplates')

    # columns= (
    #     ('', helper.draggable),
    #     ('', helper.path_checkbox),
    #     ('review_state', 'review_state', helper.translated_string()),
    #     ('Title', 'sortable_title', linked),
    #     {'column' : 'task_type',
    #      'column_title' : taskmsg(u'label_task_type', 'Task Type')},
    #     ('deadline', helper.readable_date),
    #     ('date_of_completion', readable_date_set_invisibles), # erledigt am
    #     {'column' : 'responsible',
    #      'column_title' : taskmsg(u'label_responsible_task', 'Responsible'),
    #      'transform' : readable_ogds_author},
    #     ('issuer', readable_ogds_author), # zugewiesen von
    #     {'column' : 'created',
    #      'column_title' : taskmsg(u'label_issued_date', 'issued at'),
    #      'transform': helper.readable_date },
    #     )

    types = ['opengever.tasktemplates.tasktemplate',]