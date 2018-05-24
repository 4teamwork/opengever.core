from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.task.browser.transitioncontroller import Checker
from opengever.task.browser.transitioncontroller import get_checker
from opengever.task.browser.transitioncontroller import TaskChecker
from opengever.task.interfaces import ISuccessorTaskController
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
import transaction


class TestTaskControllerChecker(FunctionalTestCase):

    def setUp(self):
        super(TestTaskControllerChecker, self).setUp()

        self.hugo = create(Builder('ogds_user')
                           .having(userid='hugo.boss',
                                   firstname='Hugo',
                                   lastname='Boss',
                                   email='hugo@boss.ch')
                           .in_group(self.org_unit.users_group))
        transaction.commit()

    def test_is_issuer(self):
        task1 = create(Builder('task').having(issuer=TEST_USER_ID))
        task2 = create(Builder('task').having(issuer='hugo.boss'))

        self.assertTrue(get_checker(task1).current_user.is_issuer)
        self.assertFalse(get_checker(task2).current_user.is_issuer)

    def test_is_issuer_checks_inbox_members_if_issuer_is_a_inbox(self):
        task1 = create(Builder('task')
                       .having(issuer=self.org_unit.inbox().id()))

        self.assertTrue(get_checker(task1).current_user.is_issuer)

        checker = Checker(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(checker.current_user.is_issuer)

    def test_is_responsible(self):
        task1 = create(Builder('task').having(responsible=TEST_USER_ID))
        task2 = create(Builder('task').having(responsible='hugo.boss'))

        self.assertTrue(get_checker(task1).current_user.is_responsible)
        self.assertFalse(get_checker(task2).current_user.is_responsible)

    def test_is_responsible_checks_inbox_members_if_issuer_is_a_inbox(self):
        task1 = create(Builder('task')
                       .having(responsible=self.org_unit.inbox().id()))

        self.assertTrue(get_checker(task1).current_user.is_responsible)

        checker = Checker(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(checker.current_user.is_responsible)

    def test_issuing_orgunit_agency_member(self):
        """Checks if the current user is member of the issuing
        orgunit's inbox_group"""

        task1 = create(Builder('task').having(issuer=TEST_USER_ID))

        self.assertTrue(
            get_checker(task1).current_user.in_issuing_orgunits_inbox_group)

        checker = Checker(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(checker.current_user.in_issuing_orgunits_inbox_group)

    def test_responsible_orgunit_agency_member(self):
        """Checks if the current user is member of the responsible
        orgunit's inbox_group"""

        task1 = create(Builder('task').having(responsible_client='client1'))

        self.assertTrue(
            get_checker(task1).current_user.in_responsible_orgunits_inbox_group)

        checker = Checker(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(
            checker.current_user.in_responsible_orgunits_inbox_group)

    def test_all_subtasks_finished(self):
        task = create(Builder('task').in_state('task-state-in-progress'))
        create(Builder('task')
               .within(task)
               .in_state('task-state-tested-and-closed'))
        create(Builder('task')
               .within(task)
               .in_state('task-state-rejected'))
        create(Builder('task')
               .within(task)
               .in_state('task-state-cancelled'))

        self.assertTrue(get_checker(task).task.all_subtasks_finished)

    def test_all_subtasks_is_NOT_finished_when_cancelled_or_resolved(self):
        task = create(Builder('task').in_state('task-state-in-progress'))
        create(Builder('task')
               .within(task)
               .in_state('task-state-resolved'))
        create(Builder('task')
               .within(task)
               .in_state('task-state-cancelled'))

        self.assertFalse(get_checker(task).task.all_subtasks_finished)

    def test_all_subtasks_finished_is_allways_true_when_no_subtask_exists(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.assertTrue(get_checker(task).task.all_subtasks_finished)

    def test_has_successors(self):
        task_with_successor = create(Builder('task'))
        task_without_successor = create(Builder('task'))
        create(Builder('task').successor_from(task_with_successor))

        self.assertTrue(get_checker(task_with_successor).task.has_successors)
        self.assertFalse(get_checker(task_without_successor).task.has_successors)

    def test_is_remote_request_checks_ogds_plugin_flag(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.assertFalse(get_checker(task).request.is_remote)

        task.REQUEST.environ['X_OGDS_AUID'] = 'rr'

        self.assertTrue(get_checker(task).request.is_remote)

    def test_is_successor_process_checks_request_for_succesor_flag(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.assertFalse(get_checker(task).request.is_successor_process)

        task.REQUEST.set('X-CREATING-SUCCESSOR', True)

        self.assertTrue(get_checker(task).request.is_successor_process)

    def test_is_assigned_to_current_admin_unit(self):
        admin_unit = create(Builder('admin_unit')
                            .id('additional'))
        create(Builder('org_unit')
               .id('additional')
               .with_default_groups()
               .having(title='Additional',
                       admin_unit=admin_unit))

        task1 = create(Builder('forwarding')
                       .having(responsible_client='client1'))
        task2 = create(Builder('forwarding')
                       .having(responsible=TEST_USER_ID,
                               issuer=TEST_USER_ID,
                               responsible_client='additional'))

        self.assertTrue(get_checker(task1).task.is_assigned_to_current_admin_unit)
        self.assertFalse(get_checker(task2).task.is_assigned_to_current_admin_unit)

    def test_all_subtasks_finished_if_predecessor_has_subtasks(self):

        # Create a pending task
        predecessor = create(
            Builder('task')
            .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
            .having(
                responsible_client='client1',
                task_type='correction',
                )
            .in_state('task-state-in-progress')
            )

        # Create a pending subtask
        create(
            Builder('task')
            .within(predecessor)
            .titled(u'Grundlagen in Vertragsentwurf \xdcberpr\xfcfen')
            .having(
                responsible_client='client1',
                task_type='correction',
            )
            .in_state('task-state-in-progress')
        )

        # Create a pending successor
        create(
            Builder('task')
            .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
            .having(
                responsible_client='client1',
                task_type='correction',
                )
            .successor_from(predecessor)
            .in_state('task-state-in-progress')
            )

        sql_successor_task = ISuccessorTaskController(
            predecessor).get_successors()[0]

        task_checker = TaskChecker(sql_successor_task)
        self.assertFalse(task_checker.all_subtasks_finished)
