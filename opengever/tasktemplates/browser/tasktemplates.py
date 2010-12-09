from five import grok
from ftw.table import helper
from opengever.tabbedview.browser.tabs import OpengeverCatalogListingTab
from opengever.tabbedview.helper import linked
from opengever.task import _ as taskmsg
from opengever.task.helper import task_type_helper
from opengever.tasktemplates import _
from opengever.tasktemplates.browser.helper import interactive_user_helper
from plone.directives import dexterity
from zope.interface import implements, Interface
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
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


class ITasktemplatesView(Interface):
    pass


class View(dexterity.DisplayForm):
    implements(ITasktemplatesView)
    grok.context(ITaskTemplate)
    grok.require('zope2.View')
    def responsible_link(self):
        info = getUtility(IContactInformation)
        task = ITaskTemplate(self.context)
        return info.render_link(task.responsible)

    def issuer_link(self):
        info = getUtility(IContactInformation)
        task = ITaskTemplate(self.context)
        return info.render_link(task.issuer)
