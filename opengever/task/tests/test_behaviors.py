from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestTaskId(FunctionalTestCase):

    def setUp(self):
        super(TestTaskId, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_is_prefixed_with_task_and_starts_at_1(self):
        task1 = create(Builder('task'))
        self.assertEquals('task-1', task1.id)

    def test_is_incremented_by_1(self):
        task1 = create(Builder('task'))
        task2 = create(Builder('task'))

        self.assertEquals('task-1', task1.id)
        self.assertEquals('task-2', task2.id)
