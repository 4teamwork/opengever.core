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

        with NightlyWorkflowSecurityUpdater(reindex_security=False) as updater:
            updater.update(
                ['opengever_workspace_todolist',
                 'opengever_period_workflow',
                 'opengever_committee_workflow',
                 'opengever_workspace_root',
                 'opengever_workspace',
                 'opengever_workspace_document',
                 'opengever_workspace_todo',
                 'opengever_committeecontainer_workflow',
                 'opengever_workspace_folder',
                 'opengever_workspace_meeting'])
