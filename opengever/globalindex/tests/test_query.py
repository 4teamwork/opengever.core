from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex.model.task import Task
from opengever.testing import FunctionalTestCase
from opengever.testing import MEMORY_DB_LAYER
from opengever.testing import obj2brain
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

    def task(self, intid, current_admin_unit, sequence_number=1, **kw):
        arguments = {'issuing_org_unit': 'rr',
                     'assigned_org_unit': 'bd'}
        arguments.update(kw)

        task = Task(intid, current_admin_unit, sequence_number=sequence_number,
                    **arguments)
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

    def test_by_id_with_existing_pair(self):
        self.task(1, 'rr')
        task2 = self.task(2, 'rr')
        self.task(2, 'bd')

        self.assertEquals(task2, Task.query.by_id(2, 'rr'))

    def test_by_id_with_NOT_existing_pair_returns_none(self):
        self.task(1, 'rr')

        self.assertEquals(None, Task.query.by_id(1, 'bd'))

    def test_task_by_ids_returns_tasks_wich_match_the_given_intid_and_adminunit(self):
        task1 = self.task(1, 'unita')
        task2 = self.task(2, 'unita')
        task3 = self.task(3, 'unitb')
        task4 = self.task(3, 'unita')

        self.assertSequenceEqual(
            [task1, task2, task4],
            Task.query.tasks_by_ids([1, 2, 3], self.admin_unit_a).all())

        self.assertSequenceEqual(
            [task3],
            Task.query.tasks_by_ids([1, 2, 3], self.admin_unit_b).all())

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


class TestFunctionalTaskQueries(FunctionalTestCase):

    def setUp(self):
        super(TestFunctionalTaskQueries, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.dossier = create(Builder('dossier'))

    def test_by_container_list_recursive_all_tasks_inside_the_given_container(self):
        create(Builder('task').within(self.portal))
        task1 = create(Builder('task').within(self.dossier))
        subtask = create(Builder('task').within(task1))

        self.assertItemsEqual(
            [task1.get_sql_object(), subtask.get_sql_object()],
            Task.query.by_container(self.dossier, self.admin_unit).all())

    def test_by_container_queries_adminunit_dependent(self):
        create(Builder('task').within(self.dossier))

        additional_org_unit = create(Builder('org_unit')
                                     .assign_users([self.user])
                                     .id(u'additional')
                                     .as_current_org_unit())

        additional_admin_unit = create(Builder('admin_unit')
                                       .id(u'additional')
                                       .as_current_admin_unit()
                                       .assign_org_units([additional_org_unit]))

        task2 = create(Builder('task').within(self.dossier))

        self.assertEquals(
            [task2.get_sql_object()],
            Task.query.by_container(self.dossier, additional_admin_unit).all())

    def test_by_brain_returns_corresponding_sql_task(self):
        task1 = create(Builder('task'))

        self.assertEquals(
            task1.get_sql_object(),
            Task.query.by_brain(obj2brain(task1)))

    def test_by_brain_queries_adminunit_dependent(self):
        create(Builder('task'))

        additional_org_unit = create(Builder('org_unit')
                                     .assign_users([self.user])
                                     .id(u'additional')
                                     .as_current_org_unit())
        additional_admin_unit = create(Builder('admin_unit')
                                       .id(u'additional')
                                       .as_current_admin_unit()
                                       .assign_org_units([additional_org_unit]))

        task = create(Builder('task'))

        self.assertEquals(
            task.get_sql_object(),
            Task.query.by_brain(obj2brain(task)))
