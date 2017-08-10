from ftw.lawgiver.tests.base import WorkflowTest
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING


class GeverWorkflowTest(WorkflowTest):

    layer = OPENGEVER_INTEGRATION_TESTING
    workflow_name = None

    def _is_base_test(self):
        if type(self) == GeverWorkflowTest:
            return True
        else:
            return super(GeverWorkflowTest, self)._is_base_test()


    @property
    def workflow_path(self):
        self.assertIsNotNone(self.workflow_name, 'No workflow_name defined.')
        return "../profiles/default/workflows/{}".format(self.workflow_name)
