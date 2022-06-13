from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import timedelta
from opengever.task.interfaces import ITaskSettings
from opengever.task.task import ITask
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderWorkflowTransition
from opengever.tasktemplates.tasktemplatefolder import ACTIVE_STATE
from opengever.tasktemplates.tasktemplatefolder import TRANSITION_ACTIVATE
from plone import api
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


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


def update_workflow_state(tasktemplatefolder, event):
    """After creation of a sub TaskTemplateFolder, we need to set its
    workflow state in the same state as its parent
    """
    if not tasktemplatefolder.is_subtasktemplatefolder():
        return

    parent = aq_parent(aq_inner(tasktemplatefolder))
    if api.content.get_state(parent) != ACTIVE_STATE:
        return

    alsoProvides(getRequest(), IDuringTaskTemplateFolderWorkflowTransition)
    api.content.transition(obj=tasktemplatefolder,
                           transition=TRANSITION_ACTIVATE)
    noLongerProvides(getRequest(), IDuringTaskTemplateFolderWorkflowTransition)
