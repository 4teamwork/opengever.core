from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from sqlalchemy.orm.exc import NoResultFound
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

    def test_restrict_checks_principals(self):
        # Responsible user is able to see
        self.login(self.regular_user)
        sql_task = self.task_in_protected_dossier.get_sql_object()
        self.assertIn(sql_task, Task.query.restrict().all())

        # Secretariat user is not able to see the task
        self.login(self.secretariat_user)
        self.assertNotIn(sql_task, Task.query.restrict().all())

    def test_restrict_query_is_distinct(self):
        """This tests checks that the result set does not return task objects
        multiple times.
        """

        self.login(self.regular_user)
        result = Task.query.restrict().all()

        self.assertEqual(len(result), len(set(result)))

    def test_restrict_checks_is_skipped_for_admins(self):
        # Responsible user is able to see
        self.login(self.administrator)
        sql_task = self.task_in_protected_dossier.get_sql_object()
        self.assertIn(sql_task, Task.query.restrict().all())

    def test_by_container_list_recursive_all_tasks_inside_the_given_container(self):
        self.login(self.regular_user)

        self.assertItemsEqual(
            [self.task.get_sql_object(),
             self.subtask.get_sql_object(),
             self.sequential_task.get_sql_object(),
             self.seq_subtask_1.get_sql_object(),
             self.seq_subtask_2.get_sql_object(),
             self.seq_subtask_3.get_sql_object(),
             self.info_task.get_sql_object(),
             self.private_task.get_sql_object()],
            Task.query.by_container(self.dossier, get_current_admin_unit()).all())

    def test_by_container_handles_similar_paths_exactly(self):
        self.login(self.regular_user)

        # manually set a similar physical path than self.task
        self.sequential_task.get_sql_object().physical_path = (
            'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-11'
            '/task-3'
        )  # Do not add commas within this grouping - this is a string!

        tasks = Task.query.by_container(self.dossier, get_current_admin_unit()).all()

        self.assertIn(self.task.get_sql_object(), tasks)
        self.assertNotIn(self.sequential_task.get_sql_object(), tasks)

    def test_by_container_queries_adminunit_dependent(self):
        self.login(self.regular_user)

        additional = create(Builder('admin_unit').id("additional"))
        self.assertItemsEqual(
            [],
            Task.query.by_container(self.dossier, additional).all())

    def test_by_brain_returns_corresponding_sql_task(self):
        self.login(self.regular_user)

        self.assertEquals(
            self.task.get_sql_object(),
            Task.query.by_brain(obj2brain(self.task)))

    def test_by_brain_queries_adminunit_dependent(self):
        self.login(self.regular_user)

        self.assertEquals(
            self.task.get_sql_object(),
            Task.query.by_brain(obj2brain(self.task)))

        # manually change admin_unit of task
        self.task.get_sql_object().admin_unit_id = 'additional'

        with self.assertRaises(NoResultFound):
            self.assertIsNone(Task.query.by_brain(obj2brain(self.task)))

    def test_subtasks_by_task_returns_all_subtask_excluding_the_given_one(self):
        self.login(self.regular_user)

        self.assertEqual(
            [self.seq_subtask_1.get_sql_object(),
             self.seq_subtask_2.get_sql_object(),
             self.seq_subtask_3.get_sql_object()],
            Task.query.subtasks_by_task(self.sequential_task.get_sql_object()).all())

    def test_subtasks_by_task_returns_empty_list_when_no_subtask_exists(self):
        self.login(self.regular_user)

        self.assertEqual(
            [],
            Task.query.subtasks_by_task(self.expired_task.get_sql_object()).all())
