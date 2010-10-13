from opengever.tabbedview.browser.tabs import OpengeverListingTab
from opengever.tabbedview.helper import linked
from ftw.table import helper
from opengever.tasktemplates.browser.helper import interactive_user_helper
from opengever.task.helper import task_type_helper
from five import grok
from opengever.task import _ as taskmsg
from opengever.tasktemplates import _


class TaskTemplates(OpengeverListingTab):
    grok.name('tabbedview_view-tasktemplates')

    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        {'column' : 'task_type',
         'column_title' : taskmsg(u'label_task_type', 'Task Type'),
         'transform': task_type_helper},
        ('issuer', interactive_user_helper),
        {'column' : 'responsible',
         'column_title' : taskmsg(u'label_responsible_task', 'Responsible'),
         'transform' : interactive_user_helper},
        {'column': 'deadline',
         'column_title': _(u"label_deadline", default=u"Deadline in Days")},
        )

    types = ['opengever.tasktemplates.tasktemplate',]
