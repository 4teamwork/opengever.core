from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task.browser.transitioncontroller import Checker
from opengever.task.browser.transitioncontroller import get_checker
from opengever.task.browser.transitioncontroller import TaskChecker
from opengever.task.interfaces import ISuccessorTaskController
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from unittest import skip


class TestTaskControllerChecker(IntegrationTestCase):

    def test_is_issuer(self):
        self.login(self.dossier_responsible)
        self.task.issuer = self.dossier_responsible.getId()
        self.task.get_sql_object().sync_with(self.task)
        self.assertTrue(get_checker(self.task).current_user.is_issuer)

        self.task.issuer = self.secretariat_user.getId()
        self.task.get_sql_object().sync_with(self.task)
        self.assertFalse(get_checker(self.task).current_user.is_issuer)

    def test_is_issuer_checks_inbox_members_if_issuer_is_a_inbox(self):
        self.login(self.regular_user)
        self.task.issuer = get_current_org_unit().inbox().id()
        self.task.get_sql_object().sync_with(self.task)
        self.assertFalse(get_checker(self.task).current_user.is_issuer)

        self.login(self.secretariat_user)
        self.assertTrue(get_checker(self.task).current_user.is_issuer)

    def test_is_responsible(self):
        self.login(self.dossier_responsible)
        self.task.responsible = self.dossier_responsible.getId()
        self.task.get_sql_object().sync_with(self.task)
        self.assertTrue(get_checker(self.task).current_user.is_responsible)

        self.task.responsible = self.regular_user.getId()
        self.task.get_sql_object().sync_with(self.task)
        self.assertFalse(get_checker(self.task).current_user.is_responsible)

    def test_is_responsible_checks_inbox_members_if_issuer_is_a_inbox(self):
        self.login(self.regular_user)
        self.task.responsible = get_current_org_unit().inbox().id()
        self.task.get_sql_object().sync_with(self.task)
        self.assertFalse(get_checker(self.task).current_user.is_responsible)

        self.login(self.secretariat_user)
        self.assertTrue(get_checker(self.task).current_user.is_responsible)

    def test_issuing_orgunit_agency_member(self):
        """Checks if the current user is member of the issuing
        orgunit's inbox_group"""
        self.login(self.secretariat_user)
        self.assertTrue(
            get_checker(self.task).current_user.in_issuing_orgunits_inbox_group)
        checker = Checker(self.task.get_sql_object(), self.request, self.secretariat_user)
        self.assertFalse(checker.current_user.in_issuing_orgunits_inbox_group)

    def test_responsible_orgunit_agency_member(self):
        """Checks if the current user is member of the responsible
        orgunit's inbox_group"""
        self.login(self.secretariat_user)
        self.assertTrue(
            get_checker(self.task).current_user.in_responsible_orgunits_inbox_group)

        # test as well without agency
        checker = Checker(self.task.get_sql_object(), self.request, self.secretariat_user)
        self.assertFalse(
            checker.current_user.in_responsible_orgunits_inbox_group)

    def test_issuing_orgunit_agency_member_with_private_task(self):
        self.login(self.secretariat_user)
        self.task.is_private = True
        self.task.get_sql_object().sync_with(self.task)

        self.assertFalse(
            get_checker(self.task).current_user.in_issuing_orgunits_inbox_group)

    def test_responsible_orgunit_agency_member_with_private_task(self):
        self.login(self.secretariat_user)
        self.task.is_private = True
        self.task.get_sql_object().sync_with(self.task)

        self.assertFalse(
            get_checker(self.task).current_user.in_responsible_orgunits_inbox_group)

    def test_all_subtasks_finished(self):
        self.login(self.dossier_responsible)
        for state in ('task-state-rejected',
                      'task-state-cancelled',
                      'task-state-tested-and-closed'):
            self.set_workflow_state(state, self.subtask)
            self.assertTrue(get_checker(self.task).task.all_subtasks_finished)

    def test_all_subtasks_is_NOT_finished_when_cancelled_or_resolved(self):
        self.login(self.dossier_responsible)

        self.set_workflow_state('task-state-resolved', self.task)
        self.assertFalse(get_checker(self.task).task.all_subtasks_finished)

        self.set_workflow_state('task-state-cancelled', self.task)
        self.assertFalse(get_checker(self.task).task.all_subtasks_finished)

    def test_all_subtasks_finished_is_allways_true_when_no_subtask_exists(self):
        self.login(self.dossier_responsible)
        self.assertTrue(get_checker(self.expired_task).task.all_subtasks_finished)

    def test_has_successors(self):
        self.login(self.dossier_responsible)
        self.register_successor(self.task, self.subtask)

        self.assertTrue(get_checker(self.task).task.has_successors)
        self.assertFalse(get_checker(self.subtask).task.has_successors)

    def test_is_remote_request_checks_ogds_plugin_flag(self):
        self.login(self.regular_user)
        self.assertFalse(get_checker(self.task).request.is_remote)
        self.task.REQUEST.environ['X_OGDS_AUID'] = 'rr'
        self.assertTrue(get_checker(self.task).request.is_remote)

    def test_is_successor_process_checks_request_for_succesor_flag(self):
        self.login(self.regular_user)
        self.assertFalse(get_checker(self.task).request.is_successor_process)
        self.task.REQUEST.set('X-CREATING-SUCCESSOR', True)
        self.assertTrue(get_checker(self.task).request.is_successor_process)

    def test_is_assigned_to_current_admin_unit(self):
        self.login(self.secretariat_user)
        self.assertTrue(get_checker(self.inbox_forwarding).task.is_assigned_to_current_admin_unit)
        additional = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit')
               .id(u'additional')
               .having(admin_unit=additional))
        self.inbox_forwarding.responsible_client = 'additional'
        self.inbox_forwarding.get_sql_object().sync_with(self.inbox_forwarding)
        self.assertFalse(get_checker(self.inbox_forwarding).task.is_assigned_to_current_admin_unit)

    def test_all_subtasks_finished_if_predecessor_has_subtasks(self):
        self.login(self.secretariat_user)

        self.set_workflow_state('task-state-in-progress', self.subtask)
        self.set_workflow_state('task-state-in-progress', self.expired_task)
        self.register_successor(self.task, self.expired_task)

        task_checker = TaskChecker(self.expired_task.get_sql_object())
        self.assertFalse(task_checker.all_subtasks_finished)
