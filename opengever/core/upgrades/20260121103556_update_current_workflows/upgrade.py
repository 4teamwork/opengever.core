from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater


class UpdateCurrentWorkflows(UpgradeStep):
    """Update current workflows.
    """
    def __call__(self):
        self.install_upgrade_profile()
        with NightlyWorkflowSecurityUpdater(reindex_security=True) as updater:
            updater.update(
                ['opengever_repository_workflow',
                 'opengever_repositoryroot_workflow',])
