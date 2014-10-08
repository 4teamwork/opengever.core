from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker


class DossierDeactivateView(grok.View):
    """ Recursively deactivate the dossier and his subdossiers.
    If some subdossiers are already resolved we return a status err msg.
    If some subdossiers are already deactivated we ignore them."""

    grok.context(IDossierMarker)
    grok.name('transition-deactivate')
    grok.require('zope2.View')

    def render(self):

        wft = getToolByName(self.context, 'portal_workflow')
        # check for resolved subdossiers
        for subdossier in self.context.get_subdossiers():

            if wft.getInfoFor(subdossier.getObject(), 'review_state') \
                    == 'dossier-state-resolved':
                IStatusMessage(self.request).add(
                    _("The Dossier can't be deactivated, the subdossier "
                      "${dossier} is already resolved",
                      mapping=dict(dossier=subdossier.Title.decode('utf-8'),)),
                    type='error')
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        # recursively resolve all dossier
        for subdossier in self.context.get_subdossiers():
            if wft.getInfoFor(subdossier.getObject(), 'review_state') \
                    != 'dossier-state-inactive':
                wft.doActionFor(
                    subdossier.getObject(), 'dossier-transition-deactivate')

        # deactivate main dossier
        wft.doActionFor(
            self.context, 'dossier-transition-deactivate')

        IStatusMessage(self.request).add(
            _("The Dossier has been deactivated"), type='info')

        return self.request.RESPONSE.redirect(self.context.absolute_url())


class DossierActivateView(grok.View):
    """View wich activate the dossiers including his subdossiers."""

    grok.context(IDossierMarker)
    grok.name('transition-activate')
    grok.require('zope2.View')

    def render(self):

        wft = getToolByName(self.context, 'portal_workflow')
        for subdossier in self.context.get_subdossiers():
            wft.doActionFor(
                subdossier.getObject(), 'dossier-transition-activate')

        # deactivate main dossier
        wft.doActionFor(
            self.context, 'dossier-transition-activate')

        IStatusMessage(self.request).add(
            _("The Dossier has been activated"), type='info')

        return self.request.RESPONSE.redirect(self.context.absolute_url())
