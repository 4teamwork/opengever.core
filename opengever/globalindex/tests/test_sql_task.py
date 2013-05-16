from opengever.globalindex.model.task import Task
from opengever.globalindex.testing import MEMORY_DB_LAYER
from sqlalchemy.exc import IntegrityError
from unittest2 import TestCase
import transaction


class TestGlobalindexTask(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestGlobalindexTask, self).setUp()

    def test_task_representation(self):
        task1 = Task(1, 'm1')
        self.layer.session.add(task1)
        self.assertEquals('<Task 1@m1>', repr(task1))

    def test_predecessor_successor_relation(self):
        task1 = Task(1, 'm1')
        task2 = Task(2, 'm1')
        self.layer.session.add(task1)
        self.layer.session.add(task2)

        task2.predecessor = task1
        self.assertEquals([task2, ], task1.successors)

    def test_mulitple_successors(self):
        task1 = Task(1, 'm1')
        task2 = Task(2, 'm1')
        task3 = Task(3, 'm1')
        self.layer.session.add(task1)
        self.layer.session.add(task2)
        self.layer.session.add(task3)

        task2.predecessor = task1
        task3.predecessor = task1

        self.assertEquals([task2, task3], task1.successors)

    def test_successor_is_not_inherited_when_chain_linking(self):
        task1 = Task(1, 'm1')
        task2 = Task(2, 'm1')
        task3 = Task(3, 'm1')
        self.layer.session.add(task1)
        self.layer.session.add(task2)
        self.layer.session.add(task3)

        task2.predecessor = task1
        task3.predecessor = task2

        self.assertEquals([task2], task1.successors)
        self.assertEquals([task3], task2.successors)

    def test_unique_id(self):
        task1 = Task(1, 'm1')
        self.layer.session.add(task1)

        with self.assertRaises(IntegrityError) as cm:
            copy_task1 = Task(1, 'm1')
            self.layer.session.add(copy_task1)
            transaction.commit()

        self.assertIn(
            '(IntegrityError) columns client_id, int_id are not unique',
            str(cm.exception))

        transaction.abort()
