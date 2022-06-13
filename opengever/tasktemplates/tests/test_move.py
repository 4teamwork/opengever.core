from ftw.builder import Builder
from ftw.builder import create
from opengever.tasktemplates.move import TaskTemplateFolderMovabiliyChecker
from opengever.testing import IntegrationTestCase
from zExceptions import Forbidden


class TestTaskTemplateFolderMovabilityChecker(IntegrationTestCase):

    def test_can_only_move_tasktemplatefolder_into_tasktemplatefolder_if_nesting_enabled(self):
        self.login(self.administrator)
        tasktemplatefolder = create(Builder('tasktemplatefolder').within(self.templates))

        with self.assertRaises(Forbidden):
            TaskTemplateFolderMovabiliyChecker(tasktemplatefolder).validate_movement(
                self.tasktemplatefolder)

        self.activate_feature('tasktemplatefolder_nesting')
        TaskTemplateFolderMovabiliyChecker(tasktemplatefolder).validate_movement(
            self.tasktemplatefolder)
