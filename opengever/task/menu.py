from five import grok
from ftw.contentmenu.interfaces import IContentmenuPostFactoryMenu
from opengever.task import _
from opengever.task.task import ITask
from zope.interface import Interface


class TaskPostFactoryMenu(grok.MultiAdapter):
    """If a task is added to another task, it is called subtask. So we need
    to change the name of the task in the add-menu if we are on a task.
    """

    grok.adapts(ITask, Interface)
    grok.implements(IContentmenuPostFactoryMenu)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, factories):
        if not ITask.providedBy(self.context):
            # use default
            return factories

        cleaned_factories = []
        for factory in factories:
            # drop mail factory
            if factory['extra']['id'] != u'ftw-mail-mail':

                if factory['title'] == u'Task':
                    factory['title'] = _(u'Subtask')
                    factory['extra']['class'] = 'icon-task-subtask'

                cleaned_factories.append(factory)

        return cleaned_factories
