from ftw.upgrade import UpgradeStep
from opengever.workspace import is_workspace_feature_enabled


class UpdateWorkflows(UpgradeStep):
    """Update workflows after removing SQL contacts permissions.
    """

    def __call__(self):
        self.install_upgrade_profile()
        if is_workspace_feature_enabled():
            to_update = [
                'opengever_workspace_todolist',
                'opengever_workspace_folder',
                'opengever_workspace',
                'opengever_workspace_document',
                'opengever_workspace_root',
                'opengever_workspace_todo']
        else:
            to_update = [
                'opengever_committeecontainer_workflow',
                'opengever_committee_workflow',
                'opengever_period_workflow']

        self.update_workflow_security(to_update, reindex_security=False)
