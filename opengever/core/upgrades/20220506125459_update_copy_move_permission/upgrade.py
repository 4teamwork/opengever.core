from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater


class UpdateCopyMovePermission(UpgradeStep):
    """Update copy move permission.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        with NightlyWorkflowSecurityUpdater(reindex_security=False) as updater:
            updater.update(['opengever_dossier_workflow'])
