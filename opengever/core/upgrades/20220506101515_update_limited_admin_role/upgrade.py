from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater


class UpdateLimitedAdminRole(UpgradeStep):
    """Update limited admin role.
    """

    def __call__(self):
        self.install_upgrade_profile()
        with NightlyWorkflowSecurityUpdater(reindex_security=False) as updater:
            updater.update(['opengever_dossier_workflow',
                            'opengever_repository_workflow',
                            'opengever_repositoryroot_workflow',
                            'opengever_templatefolder_workflow'])
