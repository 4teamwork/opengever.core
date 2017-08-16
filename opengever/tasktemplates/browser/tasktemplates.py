from ftw.table import helper
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import linked
from opengever.task import _ as taskmsg
from opengever.task.helper import task_type_helper
from opengever.tasktemplates import _
from opengever.tasktemplates.browser.helper import interactive_user_helper
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from plone.dexterity.browser.view import DefaultView
from zope.component.hooks import getSite
from zope.i18n import translate


def preselected_helper(item, value):
    if value is True:
        return translate(
            _(u'preselected_yes', default=u'Yes'),
            context=getSite().REQUEST)
    else:
        return ''


class TaskTemplates(BaseCatalogListingTab):

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

        {'column': 'task_type',
         'column_title': taskmsg(u'label_task_type', 'Task Type'),
         'transform': task_type_helper},

        {'column': 'issuer',
         'column_title': _(u'label_issuer', 'Issuer'),
         'transform': interactive_user_helper},

        {'column': 'responsible',
         'column_title': _(u'label_responsible_task', default=u'Responsible'),
         'transform': interactive_user_helper},

        {'column': 'deadline',
         'column_title': _(u"label_deadline", default=u"Deadline in Days")},

        {'column': 'preselected',
         'column_title': _(u"label_preselected", default=u"Preselect"),
         'transform': preselected_helper},
        )

    types = ['opengever.tasktemplates.tasktemplate', ]

    enabled_actions = []

    major_actions = []


class View(DefaultView):

    def responsible_link(self):
        task = ITaskTemplate(self.context)
        return interactive_user_helper(task, task.responsible)

    def issuer_link(self):
        task = ITaskTemplate(self.context)
        return interactive_user_helper(task, task.issuer)
