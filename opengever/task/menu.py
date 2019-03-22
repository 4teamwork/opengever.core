from opengever.base.menu import FilteredPostFactoryMenuWithWebactions
from opengever.task import _
from opengever.task.task import ITask
from zope.interface import Interface
from zope.component import adapter


@adapter(ITask, Interface)
class TaskPostFactoryMenu(FilteredPostFactoryMenuWithWebactions):
    """Change the name of a task that appears in the add menu of task to
    subtask.

    """
    def is_filtered(self, factory):
        return factory['extra']['id'] == u'ftw-mail-mail'

    def __call__(self, factories):
        factories = super(TaskPostFactoryMenu, self).__call__(factories)
        for factory in factories:
            if factory['title'] == u'Task':
                factory['title'] = _(u'Subtask')
                factory['extra']['class'] = 'icon-task-subtask'

        return factories
