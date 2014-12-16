from five import grok
from opengever.base.menu import FilteredPostFactoryMenu
from opengever.task import _
from opengever.task.task import ITask
from zope.interface import Interface


class TaskPostFactoryMenu(FilteredPostFactoryMenu):
    """Change the name of a task that appears in the add menu of task to
    subtask.

    """
    grok.adapts(ITask, Interface)

    def is_filtered(self, factory):
        return factory['extra']['id'] == u'ftw-mail-mail'

    def __call__(self, factories):
        factories = super(TaskPostFactoryMenu, self).__call__(factories)
        for factory in factories:
            if factory['title'] == u'Task':
                factory['title'] = _(u'Subtask')
                factory['extra']['class'] = 'icon-task-subtask'

        return factories
