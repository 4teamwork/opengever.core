from Products.CMFCore.utils import getToolByName
from ftw.upgrade import UpgradeStep


class AdjustTransitionUrls(UpgradeStep):
    """Register the download confirmation javascript."""

    def __call__(self):
        wft = getToolByName(self.portal, 'portal_workflow')
        wf = wft.getWorkflowById('opengever_dossier_workflow')
        wf.transitions.get('dossier-transition-deactivate').actbox_url \
            = "%(content_url)s/transition-deactivate"
        wf.transitions.get('dossier-transition-activate').actbox_url \
            = "%(content_url)s/transition-activate"
