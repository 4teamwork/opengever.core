from opengever.base.interfaces import ISequenceNumber
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from zope.component import getUtility


class TestTaskId(FunctionalTestCase):

    def test_is_prefixed_with_task_and_starts_at_1(self):
        task1 = Builder('task').create()
        self.assertEquals('task-1', task1.id)

    def test_is_incremented_by_1(self):
        task1 = Builder('task').create()
        task2 = Builder('task').create()

        self.assertEquals('task-1', task1.id)
        self.assertEquals('task-2', task2.id)
