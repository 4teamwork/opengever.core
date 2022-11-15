from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater


class AddTaskResponsibleRole(UpgradeStep):
    """Add task responsible role.
    """

    def __call__(self):
        self.install_upgrade_profile()
        with NightlyWorkflowSecurityUpdater(reindex_security=True) as updater:
            updater.update(
                ['opengever_dossier_workflow'])
