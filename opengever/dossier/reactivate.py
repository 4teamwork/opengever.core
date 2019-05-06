from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

MSG_SUBDOSSIER = _("It isn't possible to reactivate a sub dossier.")


class Reactivator(object):

    def __init__(self, context):
        self.context = context
        self.wft = getToolByName(self.context, 'portal_workflow')

    def get_precondition_violations(self):
        errors = []
        parent = self.context.get_parent_dossier()
        if parent:
            if self.wft.getInfoFor(parent, 'review_state') not in DOSSIER_STATES_OPEN:
                errors.append(MSG_SUBDOSSIER)
        return errors

    def reactivate(self):
        if self.get_precondition_violations():
            raise TypeError
        self._recursive_reactivate(self.context)

    def _recursive_reactivate(self, dossier):
        for subdossier in dossier.get_subdossiers():
            self._recursive_reactivate(subdossier.getObject())

        if self.wft.getInfoFor(dossier,
                               'review_state') == 'dossier-state-resolved':

            self.reset_end_date(dossier)
            self.wft.doActionFor(dossier, 'dossier-transition-reactivate')

    def reset_end_date(self, dossier):
        IDossier(dossier).end = None
        dossier.reindexObject(idxs=['end'])


class DossierReactivateView(BrowserView):

    def __call__(self):
        reactivator = Reactivator(self.context)

        # check preconditions
        errors = reactivator.get_precondition_violations()
        if errors:
            return self.show_errors(errors)

        reactivator.reactivate()
        api.portal.show_message(message=_('Dossiers successfully reactivated.'),
                                request=self.request, type='info')
        return self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def show_errors(self, errors):
        for msg in errors:
            api.portal.show_message(
                message=msg, request=self.request, type='warning')
        return self.redirect()
