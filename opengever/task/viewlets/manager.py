from five import grok
from opengever.task.task import ITask


class BeneathTask(grok.ViewletManager):
    grok.context(ITask)
    grok.name('opengever.task.beneathTask')
