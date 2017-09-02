from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.dossier.utils import get_main_dossier
from opengever.task.task import ITask
from Products.Five import BrowserView


class TaskRedirector(grok.View):
    """Redirector view which is called when creating a task.
    For maintasks it redirects to the dossier's task-tab,
    For subtasks it redirects to maintask-overview."""

    grok.context(ITask)
    grok.name('task_redirector')
    grok.require('zope2.View')

    def render(self):
        parent = aq_inner(aq_parent(self.context))
        if ITask.providedBy(parent):
            redirect_to = '%s#overview' % parent.absolute_url()
        else:
            redirect_to = '%s#tasks' % parent.absolute_url()

        return self.request.RESPONSE.redirect(redirect_to)


class RedirectToContainingMainDossier(BrowserView):
    """Redirects the user to the containing maindossier.
    """
    def __call__(self):
        self.request.RESPONSE.redirect(
            get_main_dossier(self.context).absolute_url())


class RedirectToContainingDossier(BrowserView):
    """Redirects the user to the containing dossier.
    """
    def __call__(self):
        self.request.RESPONSE.redirect(
            self.context.get_containing_dossier().absolute_url())
