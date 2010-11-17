from five import grok
from ftw.table import helper
from opengever.tabbedview.browser.tabs import OpengeverCatalogListingTab
from opengever.tabbedview.helper import linked
from opengever.task import _ as taskmsg
from opengever.task.helper import task_type_helper
from opengever.tasktemplates import _
from opengever.tasktemplates.browser.helper import interactive_user_helper


class TaskTemplates(OpengeverCatalogListingTab):
    grok.name('tabbedview_view-tasktemplates')

    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index' : 'sortable_title',
         'transform': linked},

        {'column' : 'task_type',
         'column_title' : taskmsg(u'label_task_type', 'Task Type'),
         'transform': task_type_helper},

        {'column': 'issuer',
         'column_title': _(u'label_issuer', 'Issuer'),
         'transform': interactive_user_helper},

        {'column' : 'responsible',
         'column_title' : _(u'label_responsible_task', default=u'Responsible'),
         'transform' : interactive_user_helper},

        {'column': 'deadline',
         'column_title': _(u"label_deadline", default=u"Deadline in Days")},
        )

    types = ['opengever.tasktemplates.tasktemplate',]

    enabled_actions = [
        'cut',
        'paste',
        'delete',
        ]