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

    def test_get_task_with_existing_intid_admin_unit_id_pair(self):
        self.add_task(1, 'admin1')
        self.add_task(2, 'admin1')
        task3 = self.add_task(3, 'admin2')

        self.assertEquals(task3, self.query.get_task(3, 'admin2'))

    def test_get_task_with_non_existing_intid_admin_unit_id_pair(self):
        self.add_task(1, 'admin1')

        self.assertEquals(None, self.query.get_task(1, 'admin2'))

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
        task2 = self.add_task(2, 'admin1', issuer='james.bond')
        task3 = self.add_task(3, 'admin1', issuer='james.bond')

        self.assertEquals(
            [task2, task3], self.query.get_tasks_for_issuer('james.bond'))
        self.assertEquals([], self.query.get_tasks_for_issuer('eduard'))

    def test_query_py_path(self):
        task1 = self.add_task(
            1, admin_unit_id='admin1', physical_path='test/task-1/')
        self.add_task(
            2, admin_unit_id='admin2', physical_path='test/task-1/')
        self.add_task(
            3, admin_unit_id='admin2', physical_path='test/task-20/')

        self.assertEquals(
            task1, self.query.get_task_by_path('test/task-1/', 'admin1'))
        self.assertEquals(
            None, self.query.get_task_by_path('test/task-20/', 'admin1'))
        self.assertEquals(
            None, self.query.get_task_by_path('not-existing/task-3/', 'admin1'))

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

    def add_task(self, intid, admin_unit_id='admin1',
                 issuing_org_unit_id='org1',
                 assigned_org_unit_id='org2',
                 **kwargs):
        task = Task(intid, admin_unit_id,
                    issuing_org_unit=issuing_org_unit_id,
                    assigned_org_unit=assigned_org_unit_id,
                    **kwargs)
        self.layer.session.add(task)
        return task
