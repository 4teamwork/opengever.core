from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api
from Products.statusmessages.interfaces import IStatusMessage


class DossierActivateView(grok.View):
    """View which activates the dossier including its subdossiers."""

    grok.context(IDossierMarker)
    grok.name('transition-activate')
    grok.require('zope2.View')

    def render(self):
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
            api.content.transition(obj=subdossier.getObject(),
                                   transition='dossier-transition-activate')

        # main dossier
        api.content.transition(obj=self.context,
                               transition='dossier-transition-activate')

        IStatusMessage(self.request).add(_("The Dossier has been activated"),
                                         type='info')
