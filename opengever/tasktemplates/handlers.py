from datetime import timedelta
from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.task.task import ITask
from opengever.tasktemplates.content.tasktemplate import \
    MAIN_TASK_DEADLINE_DELTA
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


@grok.subscribe(IFromTasktemplateGenerated, IObjectModifiedEvent)
def update_deadline(task, event):
    """Update the parents deadline, when a subtask deadline has changed."""
    for descr in event.descriptions:
        for attr in descr.attributes:
            if attr == 'deadline':
                parent = aq_parent(aq_inner(task))
                if ITask.providedBy(parent):
                    temp = task.deadline + timedelta(MAIN_TASK_DEADLINE_DELTA)
                    if parent.deadline < temp:
                        parent.deadline = temp
                        parent.reindexObject()
