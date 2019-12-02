from opengever.core.tests.base import GeverWorkflowTest


class TestCommitteeContainerWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_committeecontainer_workflow'


class TestCommitteeWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_committee_workflow'


class TestPeriodWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_period_workflow'


class TestWorkspaceRootWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_workspace_root'


class TestWorkspaceFolderWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_workspace_folder'


class TestWorkspaceWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_workspace'
