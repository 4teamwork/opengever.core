from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create


class TestTaskType(FunctionalTestCase):

    def test_is_no_subtask(self):
        task1 = create(Builder('task'))
        self.assertFalse(task1.is_subtask())

    def test_is_subtask(self):
        task1 = create(Builder('task'))
        subtask1 = create(Builder('task').within(task1))
        self.assertTrue(subtask1.is_subtask())

    def test_is_no_remotetask(self):
        task1 = create(Builder('task'))
        self.assertFalse(task1.is_remotetask())

    def test_is_remotetask(self):
        task1 = create(Builder('task')
                       .having(responsible_client='another client'))
        self.assertTrue(task1.is_remotetask())
