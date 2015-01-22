from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api
from Products.statusmessages.interfaces import IStatusMessage


class DossierDeactivateView(grok.View):
    """ Recursively deactivate the dossier and his subdossiers.
    If some subdossiers are already resolved we return a status err msg.
    If some subdossiers are already deactivated we ignore them."""

    grok.context(IDossierMarker)
    grok.name('transition-deactivate')
    grok.require('zope2.View')

    def render(self):
        if not self.check_preconditions():
            return self.redirect()

        # recursively deactivate all dossiers
        for subdossier in self.context.get_subdossiers():
            state = api.content.get_state(obj=subdossier.getObject())
            if state != 'dossier-state-inactive':
                api.content.transition(
                    obj=subdossier.getObject(),
                    transition=u'dossier-transition-deactivate')

        # deactivate main dossier
        api.content.transition(obj=self.context,
                               transition='dossier-transition-deactivate')

        IStatusMessage(self.request).add(
            _("The Dossier has been deactivated"), type='info')

        return self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def check_preconditions(self):
        satisfied = True

        if not self.context.is_all_checked_in():
            IStatusMessage(self.request).add(
                _(u"The Dossier can't be deactivated, not all contained"
                  "documents are checked in."), type='error')
            satisfied = False

        # check for resolved subdossiers
        for subdossier in self.context.get_subdossiers():
            state = api.content.get_state(obj=subdossier.getObject())
            if state == 'dossier-state-resolved':
                IStatusMessage(self.request).add(
                    _(u"The Dossier can't be deactivated, the subdossier "
                      "${dossier} is already resolved",
                      mapping=dict(dossier=subdossier.Title.decode('utf-8'),)),
                    type='error')
                satisfied = False

        return satisfied
