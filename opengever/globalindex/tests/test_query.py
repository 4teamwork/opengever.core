from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.globalindex.query import TaskQuery
from opengever.globalindex.testing import MEMORY_DB_LAYER
from unittest2 import TestCase
from zope.component import getUtility
from zope.component import provideUtility


class TestTaskQuery(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestTaskQuery, self).setUp()
        provideUtility(TaskQuery())
        self.query = getUtility(ITaskQuery)

    def test_get_task_with_existing_intid_clientid_pair(self):
        self.add_task(1, 'client1')
        self.add_task(2, 'client1')
        task3 = self.add_task(3, 'client2')

        self.assertEquals(task3, self.query.get_task(3, 'client2'))

    def test_get_task_with_non_existing_intid_clientid_pair(self):
        self.add_task(1, 'client1')

        self.assertEquals(None, self.query.get_task(1, 'client2'))

    def test_query_by_existing_responsible(self):
        task1 = self.add_task(1, responsible='hugo.boss')
        task2 = self.add_task(2, responsible='james.bond')
        task3 = self.add_task(3, responsible='hugo.boss')

        self.assertEquals([task1, task3],
            self.query.get_tasks_for_responsible('hugo.boss'))
        self.assertEquals([task2],
            self.query.get_tasks_for_responsible('james.bond'))

    def test_query_by_not_existing_responsible(self):
        self.add_task(1, responsible='hugo.boss')

        self.assertEquals([],
            self.query.get_tasks_for_responsible('eduard'))

    def test_query_by_issuer(self):
        self.add_task(1, issuer='hugo.boss')
        task2 = self.add_task(2, 'client1', issuer='james.bond')
        task3 = self.add_task(3, 'client1', issuer='james.bond')

        self.assertEquals(
            [task2, task3], self.query.get_tasks_for_issuer('james.bond'))
        self.assertEquals([], self.query.get_tasks_for_issuer('eduard'))

    def test_query_py_path(self):
        task1 = self.add_task(
            1, clientid='client1', physical_path='test/task-1/')
        self.add_task(
            2, clientid='client2', physical_path='test/task-1/')
        self.add_task(
            3, clientid='client2', physical_path='test/task-20/')

        self.assertEquals(
            task1, self.query.get_task_by_path('test/task-1/', 'client1'))
        self.assertEquals(
            None, self.query.get_task_by_path('test/task-20/', 'client1'))
        self.assertEquals(
            None, self.query.get_task_by_path('not-existing/task-3/', 'client1'))

    def test_query_by_paths(self):
        task1 = self.add_task(1, physical_path='test/task-1/')
        task2 = self.add_task(2, physical_path='test/task-5/')
        task3 = self.add_task(3, physical_path='test/task-20/')

        self.assertEquals(
            [task1, task2, task3],
            self.query.get_tasks_by_paths(
                ['test/task-1/', 'test/task-5/', 'test/task-20/'])
        )
        self.assertEquals(
            [task2, task3],
            self.query.get_tasks_by_paths(
                ['not-existing/task-1/', 'test/task-5/', 'test/task-20/'])
        )

    def add_task(self, intid, clientid='client1', **kwargs):
        task = Task(intid, clientid)
        if kwargs.get('responsible'):
            task.responsible = kwargs.get('responsible')
        if kwargs.get('issuer'):
            task.issuer = kwargs.get('issuer')
        if kwargs.get('physical_path'):
            task.physical_path = kwargs.get('physical_path')

        self.layer.session.add(task)
        return task
