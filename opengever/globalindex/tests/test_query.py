from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex.model.task import Task
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestTaskQueries(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestTaskQueries, self).setUp()

        self.session = self.layer.session

        rr = create(Builder('org_unit').id('rr'))
        bd = create(Builder('org_unit').id('bd'))
        afi = create(Builder('org_unit').id('afi'))

        self.admin_unit_a = create(Builder('admin_unit')
                                   .id('unita')
                                   .assign_org_units([rr, bd]))
        self.admin_unit_b = create(Builder('admin_unit')
                                   .id('unitb')
                                   .assign_org_units([afi]))

    def task(self, intid, current_admin_unit, **kw):
        arguments = {'issuing_org_unit': 'rr',
                     'assigned_org_unit': 'bd'}
        arguments.update(kw)

        task = Task(intid, current_admin_unit, **arguments)
        self.session.add(task)
        return task

    def test_users_tasks_lists_only_tasks_assigned_to_current_user(self):
        task1 = self.task(1, 'rr', responsible='hugo.boss')
        task2 = self.task(2, 'bd', responsible='tommy.hilfiger')
        task3 = self.task(3, 'sb', responsible='hugo.boss')

        self.assertSequenceEqual(
            [task1, task3],
            Task.query.users_tasks('hugo.boss').all())

        self.assertSequenceEqual(
            [task2],
            Task.query.users_tasks('tommy.hilfiger').all())

    def test_issued_task_lists_only_task_issued_by_the_current_user(self):
        task1 = self.task(1, 'rr', issuer='hugo.boss')
        task2 = self.task(2, 'bd', issuer='tommy.hilfiger')
        task3 = self.task(3, 'sb', issuer='hugo.boss')

        self.assertSequenceEqual(
            [task1, task3],
            Task.query.users_issued_tasks('hugo.boss').all())

        self.assertSequenceEqual(
            [task2],
            Task.query.users_issued_tasks('tommy.hilfiger').all())

    def test_task_by_id_returns_tasks_wich_match_the_given_intid_and_adminunit(self):
        task1 = self.task(1, 'unita')
        task2 = self.task(2, 'unita')
        task3 = self.task(3, 'unitb')
        task4 = self.task(3, 'unita')

        self.assertSequenceEqual(
            [task1, task2, task4],
            Task.query.tasks_by_id([1, 2, 3], self.admin_unit_a).all())

        self.assertSequenceEqual(
            [task3],
            Task.query.tasks_by_id([1, 2, 3], self.admin_unit_b).all())

    def test_all_admin_unit_tasks_list_tasks_assigned_to_a_current_admin_units_org_unit(self):
        task1 = self.task(1, 'unita', assigned_org_unit='rr')
        task2 = self.task(2, 'unitb', assigned_org_unit='afi')
        task3 = self.task(3, 'unita', assigned_org_unit='bd')

        self.assertItemsEqual(
            [task1, task3],
            Task.query.all_admin_unit_tasks(self.admin_unit_a).all())

        self.assertItemsEqual(
            [task2],
            Task.query.all_admin_unit_tasks(self.admin_unit_b).all())

    def test_all_issued_tasks_lists_all_tasks_created_on_given_admin_unit(self):
        task1 = self.task(1, 'unita', assigned_org_unit='rr')
        task2 = self.task(2, 'unitb', assigned_org_unit='afi')
        task3 = self.task(3, 'unita', assigned_org_unit='bd')
        task4 = self.task(4, 'unita', assigned_org_unit='afi')

        self.assertItemsEqual(
            [task1, task3, task4],
            Task.query.all_issued_tasks(self.admin_unit_a).all())

        self.assertItemsEqual(
            [task2],
            Task.query.all_issued_tasks(self.admin_unit_b).all())
