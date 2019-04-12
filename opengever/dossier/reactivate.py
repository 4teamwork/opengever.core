from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class Reactivator(object):

    def __init__(self, context):
        self.context = context
        self.wft = getToolByName(self.context, 'portal_workflow')

    def is_reactivate_possible(self):
        parent = self.context.get_parent_dossier()
        if parent:
            if self.wft.getInfoFor(parent, 'review_state') not in DOSSIER_STATES_OPEN:
                return False
        return True

    def reactivate(self):
        if not self.is_reactivate_possible():
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
        ptool = getToolByName(self, 'plone_utils')

        reactivator = Reactivator(self.context)

        # check preconditions
        if reactivator.is_reactivate_possible():
            reactivator.reactivate()
            ptool.addPortalMessage(_('Dossiers successfully reactivated.'),
                                   type="info")
            self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            ptool.addPortalMessage(
                _("It isn't possible to reactivate a sub dossier."),
                type="warning")
            self.request.RESPONSE.redirect(self.context.absolute_url())
