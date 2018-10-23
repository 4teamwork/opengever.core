from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from plone import api
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class TestTaskQueries(IntegrationTestCase):

    def test_in_pending_state_returns_only_pending_tasks(self):
        self.login(self.regular_user)

        pending_tasks = Task.query.in_pending_state().all()

        self.assertIn(self.task.get_sql_object(), pending_tasks)
        self.assertIn(self.subtask.get_sql_object(), pending_tasks)
        self.assertIn(self.task.get_sql_object(), pending_tasks)

        self.assertNotIn(self.seq_subtask_2.get_sql_object(), pending_tasks)

    def test_users_tasks_lists_only_tasks_assigned_to_current_user(self):
        self.login(self.regular_user)

        self.assertItemsEqual(
            [self.meeting_task.get_sql_object(),
             self.meeting_subtask.get_sql_object()],
            Task.query.users_tasks(self.dossier_responsible.id).all())

    def test_issued_task_lists_only_task_issued_by_the_current_user(self):
        self.login(self.regular_user)

        self.assertItemsEqual(
            [self.sequential_task.get_sql_object()],
            Task.query.users_issued_tasks(self.regular_user.id).all())

        self.assertItemsEqual(
            [self.seq_subtask_1.get_sql_object(),
             self.seq_subtask_2.get_sql_object()],
            Task.query.users_issued_tasks(self.secretariat_user.id).all())

    def test_by_intid_with_existing_pair(self):
        self.login(self.regular_user)

        intid = getUtility(IIntIds).getId(self.task)
        self.assertEquals(self.task.get_sql_object(),
                          Task.query.by_intid(intid, 'plone'))

    def test_by_intid_with_NOT_existing_pair_returns_none(self):
        self.login(self.regular_user)
        self.assertIsNone(None, Task.query.by_intid(1, 'bd'))

    def test_task_by_oguid_returns_correct_task_with_oguid_instance_param(self):
        self.login(self.regular_user)

        oguid = Oguid.for_object(self.task)
        self.assertEqual(self.task.get_sql_object(), Task.query.by_oguid(oguid))

    def test_task_by_oguid_returns_correct_task_with_string_param(self):
        self.login(self.regular_user)

        oguid = Oguid.for_object(self.task)
        self.assertEqual(self.task.get_sql_object(), Task.query.by_oguid(oguid.id))

    def test_task_by_oguid_returns_non_for_unknown_oguids(self):
        self.login(self.regular_user)

        self.assertIsNone(Task.query.by_oguid('theanswer:42'))

    def test_py_path(self):
        self.login(self.regular_user)

        self.assertEquals(self.task.get_sql_object(),
                          Task.query.by_path(self.task.get_physical_path(), 'plone'))

    def test_py_path_returns_none_for_not_existing_task(self):
        self.login(self.regular_user)

        self.assertEquals(None, Task.query.by_path('test/not-existng/', 'plone'))

    def test_by_ids_returns_tasks_wich_match_the_given_id(self):
        self.login(self.regular_user)

        tasks = [self.task, self.subtask, self.meeting_subtask]

        self.assertEquals(
            [task.get_sql_object() for task in tasks],
            Task.query.by_ids([task.get_sql_object().id for task in tasks]))

    def test_by_assigned_org_unit(self):
        self.login(self.regular_user)

        additional = self.add_additional_org_unit()

        self.task.get_sql_object().assigned_org_unit = additional.id()
        self.meeting_subtask.get_sql_object().assigned_org_unit = additional.id()

        self.assertItemsEqual(
            [self.task.get_sql_object(), self.meeting_subtask.get_sql_object()],
            Task.query.by_assigned_org_unit(additional).all())

    def test_by_issuing_org_unit(self):
        self.login(self.regular_user)

        additional = self.add_additional_org_unit()

        self.task.get_sql_object().issuing_org_unit = additional.id()
        self.meeting_subtask.get_sql_object().issuing_org_unit = additional.id()

        self.assertEquals(
            [self.task.get_sql_object(), self.meeting_subtask.get_sql_object()],
            Task.query.by_issuing_org_unit(additional).all())

    def test_all_issued_tasks_lists_all_tasks_created_on_given_admin_unit(self):
        self.login(self.regular_user)

        additional = create(Builder('admin_unit').id("additional"))

        tasks = [self.task.get_sql_object(),
                 self.meeting_subtask.get_sql_object()]

        self.task.get_sql_object().admin_unit_id = additional.id()
        self.meeting_subtask.get_sql_object().admin_unit_id = additional.id()

        self.assertItemsEqual(
            tasks, Task.query.all_issued_tasks(additional).all())


class TestFunctionalTaskQueries(FunctionalTestCase):

    def setUp(self):
        super(TestFunctionalTaskQueries, self).setUp()

        self.dossier = create(Builder('dossier'))

    def test_by_container_list_recursive_all_tasks_inside_the_given_container(self):
        create(Builder('task').within(self.portal))
        task1 = create(Builder('task').within(self.dossier))
        subtask = create(Builder('task').within(task1))

        self.assertItemsEqual(
            [task1.get_sql_object(), subtask.get_sql_object()],
            Task.query.by_container(self.dossier, self.admin_unit).all())

    def test_by_container_handles_similar_paths_exactly(self):
        task1 = create(Builder('task').within(self.dossier))

        dossier_11 = create(Builder('dossier').titled(u'Dossier 11'))
        dossier_11 = api.content.rename(obj=dossier_11, new_id='dossier-11')
        create(Builder('task').within(dossier_11))

        self.assertItemsEqual(
            [task1.get_sql_object()],
            Task.query.by_container(self.dossier, self.admin_unit).all())

    def test_by_container_queries_adminunit_dependent(self):
        create(Builder('task').within(self.dossier))

        additional_admin_unit = create(Builder('admin_unit')
                                       .id(u'additional')
                                       .having(title='foo')
                                       .as_current_admin_unit())

        create(Builder('org_unit')
               .having(admin_unit=additional_admin_unit)
               .assign_users([self.user])
               .id(u'additional')
               .as_current_org_unit())

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

        additional_admin_unit = create(
            Builder('admin_unit')
            .id(u'additional')
            .as_current_admin_unit())

        create(Builder('org_unit')
               .having(admin_unit=additional_admin_unit)
               .assign_users([self.user])
               .id(u'additional')
               .as_current_org_unit())

        task = create(Builder('task'))

        self.assertEquals(
            task.get_sql_object(),
            Task.query.by_brain(obj2brain(task)))

    def test_subtasks_by_task_returns_all_subtask_excluding_the_given_one(self):
        task1 = create(Builder('task'))
        task2 = create(Builder('task'))

        subtask1 = create(Builder('task').within(task1))
        subtask3 = create(Builder('task').within(task1))
        create(Builder('task').within(task2))

        self.assertEqual(
            [subtask1.get_sql_object(), subtask3.get_sql_object()],
            Task.query.subtasks_by_task(task1.get_sql_object()).all())

    def test_subtasks_by_task_returns_empty_list_when_no_subtask_exists(self):
        task1 = create(Builder('task'))

        self.assertEqual(
            [],
            Task.query.subtasks_by_task(task1.get_sql_object()).all())
