from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater


class FixDossierPermissionsForTaskResponsible(UpgradeStep):
    """Fix dossier permissions for task responsible.
    """

    def __call__(self):
        self.install_upgrade_profile()
        with NightlyWorkflowSecurityUpdater(reindex_security=False) as updater:
            updater.update(
                ['opengever_dossier_workflow'])
