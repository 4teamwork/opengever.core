from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.task.task import ITask


class TaskRedirector(grok.View):
    """Redirector view which is called when creating a task.
    For maintasks it redirects to the dossier's task-tab,
    For subtasks it redirects to maintask-overview."""

    grok.context(ITask)
    grok.name('task_redirector')

    def render(self):
        parent = aq_inner(aq_parent(self.context))
        if ITask.providedBy(parent):
            redirect_to = '%s#overview' % parent.absolute_url()
        else:
            redirect_to = '%s#tasks' % parent.absolute_url()

        return self.request.RESPONSE.redirect(redirect_to)
