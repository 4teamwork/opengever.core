from lxml import etree
from pkg_resources import resource_filename
from unittest import TestCase
import os


class TestWorkflowIds(TestCase):

    default_profiles_path = resource_filename("opengever.core", "profiles/default")
    workflow_dir_path = resource_filename("opengever.core", "profiles/default/workflows")

    def get_workflow_directories(self):
        workflow_dirnames = []
        for dirname in os.listdir(self.workflow_dir_path):
            if os.path.isdir(os.path.join(self.workflow_dir_path, dirname)):
                workflow_dirnames.append(dirname)
        return workflow_dirnames

    def test_workflow_ids_match_path(self):
        workflow_dirnames = self.get_workflow_directories()
        workflow_ids = []
        for workflow_dirname in workflow_dirnames:
            workflow_xml = etree.parse(
                os.path.join(self.workflow_dir_path, workflow_dirname, "definition.xml"))
            workflow_ids.append(workflow_xml.getroot().attrib.get('workflow_id'))
        self.assertEqual(workflow_dirnames, workflow_ids,
                         "Workflow ID should match the directory name")

    def test_all_workflows_are_registered(self):
        """ This does not necessarily have to be true, as we could be overriding
        an already existing workflow. For now it is true, and it makes sure we
        do not forget to register a workflow in the future.
        """
        workflow_dirnames = self.get_workflow_directories()
        workflow_xml = etree.parse(os.path.join(self.default_profiles_path,
                                                "workflows.xml"))
        workflow_names = []
        for workflow in workflow_xml.getroot().findall("object"):
            workflow_names.append(workflow.attrib.get("name"))
        self.assertItemsEqual(workflow_dirnames, workflow_names,
                              "All workflows should be registered in worklows.xml"
                              "with a name corresponding to the directory name")
