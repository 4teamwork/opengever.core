from DateTime import DateTime
from ftw.upgrade import UpgradeStep
from ftw.upgrade.workflow import WorkflowChainUpdater
from plone import api


class RemoveDeactivateStateForPrivateDossiers(UpgradeStep):
    """Remove deactivate state for private dossiers.
    """

    def __call__(self):
        query = {'portal_type': 'opengever.private.dossier',
                 'review_state': 'dossier-state-inactive'}

        wf_tool = api.portal.get_tool('portal_workflow')

        for obj in self.objects(query, 'Migrate deactivated private dossiers'):

            wf_tool.setStatusOf(
                'opengever_private_dossier_workflow',
                obj,
                {'review_state': 'dossier-state-active',
                 'action': 'systemupdate',
                 'actor': 'system',
                 'comments': '',
                 'time': DateTime()})
            obj.reindexObject(idxs=['review_state'])
