from opengever.globalindex.model.task import Task
from opengever.testing import MEMORY_DB_LAYER
from sqlalchemy.exc import IntegrityError
from unittest2 import TestCase
import transaction


class TestGlobalindexTask(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestGlobalindexTask, self).setUp()

    def _create_task(self, int_id=1, admin_unit_id='m1',
                     issuing_org_unit='org', assigned_org_unit='org',
                     task_type='direct-execution'):
        return Task(int_id, admin_unit_id, issuing_org_unit=issuing_org_unit,
                    assigned_org_unit=assigned_org_unit, task_type=task_type)

    def test_task_representation(self):
        task1 = self._create_task()
        self.layer.session.add(task1)
        self.assertEquals('<Task 1@m1>', repr(task1))

    def test_predecessor_successor_relation(self):
        task1 = self._create_task()
        task2 = self._create_task(2)
        self.layer.session.add(task1)
        self.layer.session.add(task2)

        task2.predecessor = task1
        self.assertEquals([task2, ], task1.successors)

    def test_mulitple_successors(self):
        task1 = self._create_task()
        task2 = self._create_task(2)
        task3 = self._create_task(3)
        self.layer.session.add(task1)
        self.layer.session.add(task2)
        self.layer.session.add(task3)

        task2.predecessor = task1
        task3.predecessor = task1

        self.assertEquals([task2, task3], task1.successors)

    def test_successor_is_not_inherited_when_chain_linking(self):
        task1 = self._create_task()
        task2 = self._create_task(2)
        task3 = self._create_task(3)
        self.layer.session.add(task1)
        self.layer.session.add(task2)
        self.layer.session.add(task3)

        task2.predecessor = task1
        task3.predecessor = task2

        self.assertEquals([task2], task1.successors)
        self.assertEquals([task3], task2.successors)

    def test_unique_id(self):
        task1 = self._create_task()
        self.layer.session.add(task1)

        with self.assertRaises(IntegrityError) as cm:
            copy_task1 = self._create_task()
            self.layer.session.add(copy_task1)
            transaction.commit()

        self.assertIn(
            '(IntegrityError) columns admin_unit_id, int_id are not unique',
            str(cm.exception))

        transaction.abort()

    def test_is_forwarding(self):
        forwarding = self._create_task(1, task_type='forwarding_task_type')
        task = self._create_task(2, task_type='direct-execution')

        self.layer.session.add(forwarding)
        self.layer.session.add(task)

        self.assertTrue(forwarding.is_forwarding)
        self.assertFalse(task.is_forwarding)
