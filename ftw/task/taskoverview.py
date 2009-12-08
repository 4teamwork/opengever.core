from five import grok
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from ftw.table import helper

class MyTasks(OpengeverListingTab):
    grok.name('tabbedview_view-mytasks')
    columns= (
                ('', helper.draggable),
                ('', helper.path_checkbox),
                ('Title', helper.linked),
                ('deadline', helper.readable_date),
                ('responsible', helper.readable_author),
                ('review_state', 'review_state', helper.translated_string()),
            )
    types = ['ftw.task.task',]

class IssuedTasks(OpengeverListingTab):
    grok.name('tabbedview_view-issuedtasks')
    columns= (
                ('', helper.draggable),
                ('', helper.path_checkbox),
                ('Title', helper.linked),
                ('deadline', helper.readable_date),
                ('responsible', helper.readable_author),
                ('review_state', 'review_state', helper.translated_string()),
            )
    types = ['ftw.task.task',]
    
