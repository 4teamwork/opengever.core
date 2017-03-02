from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.dossier import IDossier
from plone import api
from datetime import date


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
        self.set_end_date(self.context)
        api.content.transition(obj=self.context,
                               transition='dossier-transition-deactivate')

        api.portal.show_message(
            _("The Dossier has been deactivated"), self.request, type='info')

        return self.redirect()

    def set_end_date(self, dossier):
        if not IDossier(dossier).end:
            IDossier(dossier).end = date.today()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def check_preconditions(self):
        satisfied = True

        if not self.context.is_all_checked_in():
            api.portal.show_message(
                _(u"The Dossier can't be deactivated, not all contained"
                  "documents are checked in."), self.request, type='error')
            satisfied = False

        if self.context.has_active_proposals():
            api.portal.show_message(
                _(u"The Dossier can't be deactivated, it contains active "
                  "proposals."), self.request, type='error')
            satisfied = False

        # check for resolved subdossiers
        for subdossier in self.context.get_subdossiers():
            state = api.content.get_state(obj=subdossier.getObject())
            if state == 'dossier-state-resolved':
                msg = _(u"The Dossier can't be deactivated, the subdossier "
                       "${dossier} is already resolved",
                       mapping=dict(dossier=subdossier.Title.decode('utf-8')))
                api.portal.show_message(msg, self.request, type='error')

                satisfied = False

        if self.context.has_active_tasks():
            satisfied = False
            api.portal.show_message(
                _(u"The Dossier can't be deactivated, not all contained "
                  "tasks are in a closed state."),
                self.request, type='error')

        return satisfied
