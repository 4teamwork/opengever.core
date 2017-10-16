from opengever.dossier import _
from plone import api
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class DossierActivateView(BrowserView):
    """View which activates the dossier including its subdossiers."""

    def __call__(self):
        if self.check_preconditions():
            self.activate()

        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def check_preconditions(self):
        satisfied = True
        if self.context.is_subdossier():
            state = api.content.get_state(self.context.get_parent_dossier())
            if state == 'dossier-state-inactive':
                satisfied = False
                IStatusMessage(self.request).add(
                    _("This subdossier can't be activated,"
                      "because the main dossiers is inactive"), type='error')

        return satisfied

    def activate(self):
        # subdossiers
        for subdossier in self.context.get_subdossiers():
            subdossier.getObject().activate()

        # main dossier
        self.context.activate()

        IStatusMessage(self.request).add(_("The Dossier has been activated"),
                                         type='info')
