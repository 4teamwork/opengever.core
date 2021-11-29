from ftw.lawgiver.interfaces import IWorkflowGenerator
from ftw.lawgiver.wdl.interfaces import IWorkflowSpecificationParser
from opengever.core.tests.base import GeverWorkflowTest
from zope.component import getUtility


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


class TestWorkspaceDocumentWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_workspace_document'


class TestWorkspaceMeetingWorkflow(GeverWorkflowTest):
    workflow_name = 'opengever_workspace_meeting'

    def test_workflow_definition_up_to_date(self):
        parser = getUtility(IWorkflowSpecificationParser)

        path = self.get_specification_path()
        with open(path) as spec_file:
            spec = parser(spec_file, path=path)

        with open(self.get_path('result.xml'), 'w+') as result_file:
            generator = getUtility(IWorkflowGenerator)
            generator(self.get_name(), spec).write(result_file)
            result_file.seek(0)
            result = result_file.read()

        with open(self.get_path('definition.xml')) as expected_file:
            definition = expected_file.read()

            # We have to override these permissions, because the lawgiver
            # does not allow to set the permissions with acquire="True" in one state,
            # but acquire="False" in another state.
            # Since a workspace can be deactivated, we want to get these permissions
            # from the workspace if the meeting is open, if the meeting is closed,
            # we want to set the permission ourselves.
            modify_permission = '<permission-map name="Modify portal content" acquired="True"/>'
            self.assertIn(modify_permission, definition)
            definition = definition.replace(
                modify_permission,
                '<permission-map name="Modify portal content" acquired="False">'
                '<permission-role>Administrator</permission-role>'
                '<permission-role>WorkspaceAdmin</permission-role>'
                '<permission-role>WorkspaceMember</permission-role></permission-map>')

            add_permission = '<permission-map name="Add portal content" acquired="True"/>'
            self.assertIn(add_permission, definition)
            definition = definition.replace(
                add_permission,
                '<permission-map name="Add portal content" acquired="False">'
                '<permission-role>Administrator</permission-role>'
                '<permission-role>WorkspaceAdmin</permission-role>'
                '<permission-role>WorkspaceMember</permission-role></permission-map>')

            delete_permission = '<permission-map name="opengever.workspace: '\
                                'Delete Workspace Meeting Agenda Items" acquired="True"/>'
            self.assertIn(delete_permission, definition)
            definition = definition.replace(
                delete_permission,
                '<permission-map name="opengever.workspace: Delete Workspace Meeting Agenda Items" '\
                'acquired="False">'
                '<permission-role>Administrator</permission-role>'
                '<permission-role>WorkspaceAdmin</permission-role>'
                '<permission-role>WorkspaceMember</permission-role></permission-map>')

            self.assert_definition_xmls(definition, result)
