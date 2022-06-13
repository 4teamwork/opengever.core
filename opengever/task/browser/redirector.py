from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.utils import get_main_dossier
from opengever.task.task import ITask
from Products.Five import BrowserView


class TaskRedirector(BrowserView):
    """Redirector view which is called when creating a task.
    For maintasks it redirects to the dossier's task-tab,
    For subtasks it redirects to maintask-overview."""

    def __call__(self):
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
            "?".join([
                get_main_dossier(self.context).absolute_url(),
                self.request["QUERY_STRING"]
            ])
        )


class RedirectToContainingDossier(BrowserView):
    """Redirects the user to the containing dossier.
    """
    def __call__(self):
        url_parts = [self.context.get_containing_dossier().absolute_url()]
        qs = self.request['QUERY_STRING']
        if qs:
            url_parts.append(qs)
        redirect_url = '?'.join(url_parts)

        return self.request.RESPONSE.redirect(redirect_url)
