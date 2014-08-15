from ftw.builder import Builder
from ftw.builder import create
from opengever.task.browser.transitioncontroller import Conditions
from opengever.task.browser.transitioncontroller import get_conditions
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskControllerConditions(FunctionalTestCase):

    def setUp(self):
        super(TestTaskControllerConditions, self).setUp()

        self.hugo = create(Builder('ogds_user')
                           .having(userid='hugo.boss',
                                   firstname='Hugo',
                                   lastname='Boss',
                                   email='hugo@boss.ch')
                           .in_group(self.org_unit.inbox_group()))

    def test_is_issuer(self):
        task1 = create(Builder('task').having(issuer=TEST_USER_ID))
        task2 = create(Builder('task').having(issuer='hugo.boss'))

        self.assertTrue(get_conditions(task1).is_issuer)
        self.assertFalse(get_conditions(task2).is_issuer)

    def test_is_issuer_checks_inbox_members_if_issuer_is_a_inbox(self):
        task1 = create(Builder('task')
                       .having(issuer=self.org_unit.inbox().id()))

        self.assertTrue(get_conditions(task1).is_issuer)

        conditions = Conditions(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(conditions.is_issuer)

    def test_is_responsible(self):
        task1 = create(Builder('task').having(responsible=TEST_USER_ID))
        task2 = create(Builder('task').having(responsible='hugo.boss'))

        self.assertTrue(get_conditions(task1).is_responsible)
        self.assertFalse(get_conditions(task2).is_responsible)

    def test_is_responsible_checks_inbox_members_if_issuer_is_a_inbox(self):
        task1 = create(Builder('task')
                       .having(responsible=self.org_unit.inbox().id()))

        self.assertTrue(get_conditions(task1).is_responsible)

        conditions = Conditions(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(conditions.is_responsible)

    def test_issuing_orgunit_agency_member(self):
        """Checks if the current user is member of the issuing
        orgunit's inbox_group"""

        task1 = create(Builder('task').having(issuer=TEST_USER_ID))

        self.assertTrue(
            get_conditions(task1).is_issuing_orgunit_agency_member)

        condition = Conditions(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(condition.is_issuing_orgunit_agency_member)

    def test_responsible_orgunit_agency_member(self):
        """Checks if the current user is member of the responsible
        orgunit's inbox_group"""

        task1 = create(Builder('task').having(responsible_client='client1'))

        self.assertTrue(
            get_conditions(task1).is_responsible_orgunit_agency_member)

        condition = Conditions(task1.get_sql_object(), self.request, self.hugo)
        self.assertFalse(condition.is_responsible_orgunit_agency_member)

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

        self.assertTrue(get_conditions(task).all_subtasks_finished)

    def test_all_subtasks_finished(self):
        task = create(Builder('task').in_state('task-state-in-progress'))
        create(Builder('task')
               .within(task)
               .in_state('task-state-resolved'))
        create(Builder('task')
               .within(task)
               .in_state('task-state-cancelled'))

        self.assertFalse(get_conditions(task).all_subtasks_finished)

    def test_all_subtasks_finished_is_allways_true_when_no_subtask_exists(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.assertTrue(get_conditions(task).all_subtasks_finished)

    def test_has_successors(self):
        task_with_successor = create(Builder('task'))
        task_without_successor = create(Builder('task'))
        create(Builder('task').successor_from(task_with_successor))

        self.assertTrue(get_conditions(task_with_successor).has_successors)
        self.assertFalse(get_conditions(task_without_successor).has_successors)

    def test_is_remote_request_checks_ogds_plugin_flag(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.assertFalse(get_conditions(task).is_remote_request)

        task.REQUEST.environ['X_OGDS_AUID'] = 'rr'

        self.assertTrue(get_conditions(task).is_remote_request)

    def test_is_successor_process_checks_request_for_succesor_flag(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.assertFalse(get_conditions(task).is_successor_process)

        task.REQUEST.set('X-CREATING-SUCCESSOR', True)

        self.assertTrue(get_conditions(task).is_successor_process)

    def test_is_assigned_to_current_admin_unit(self):
        org_unit = create(Builder('org_unit')
                         .id('additional')
                         .having(title='Additional'))
        create(Builder('admin_unit')
               .id('additional')
               .wrapping_org_unit(org_unit))

        task1 = create(Builder('forwarding')
                       .having(responsible_client='client1'))
        task2 = create(Builder('forwarding')
                       .having(responsible_client='additional'))

        self.assertTrue(get_conditions(task1).is_assigned_to_current_admin_unit)
        self.assertFalse(get_conditions(task2).is_assigned_to_current_admin_unit)
