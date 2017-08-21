from Acquisition import aq_inner, aq_parent
from datetime import timedelta
from opengever.task.interfaces import ITaskSettings
from opengever.task.task import ITask
from plone import api


def update_deadline(task, event):
    """Update the parents deadline, when a subtask deadline has changed."""
    for descr in event.descriptions:
        for attr in descr.attributes:
            if attr == 'deadline':
                parent = aq_parent(aq_inner(task))
                if ITask.providedBy(parent):
                    offset = api.portal.get_registry_record(
                        'deadline_timedelta', interface=ITaskSettings)
                    temp = task.deadline + timedelta(offset)
                    if parent.deadline < temp:
                        parent.deadline = temp
                        parent.reindexObject()
