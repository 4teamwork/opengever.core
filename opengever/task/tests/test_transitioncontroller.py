from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.task.browser.accept.utils import accept_task_with_successor
from opengever.task.browser.transitioncontroller import TaskTransitionController
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from opengever.testing import IntegrationTestCase
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides
import unittest


class Bunch(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeChecker(object):

    def __init__(self, is_issuer=False, is_responsible=False,
                 all_subtasks_finished=False, has_successors=False,
                 is_remote_request=False,
                 issuing_agency=False, responsible_agency=False,
                 successor_process=False, current_admin_unit_assigned=False,
                 is_administrator=False, parent_task_is_in_progress=False):

        self.current_user = Bunch(
            is_issuer=is_issuer,
            is_responsible=is_responsible,
            is_administrator=is_administrator,
            in_issuing_orgunits_inbox_group=issuing_agency,
            in_responsible_orgunits_inbox_group=responsible_agency)

        self.task = Bunch(
            all_subtasks_finished=all_subtasks_finished,
            has_successors=has_successors,
            is_assigned_to_current_admin_unit=current_admin_unit_assigned,
            parent_task_is_in_progress=parent_task_is_in_progress)

        self.request = Bunch(
            is_remote=is_remote_request,
            is_successor_process=successor_process)


class FakeTask(object):
    def __init__(self, category):
        self._category = category

    @property
    def task_type_category(self):
        return self._category


class BaseTransitionGuardTests(unittest.TestCase):
    task_type_category = 'bidirectional_by_value'

    @property
    def controller(self):
        task = FakeTask(self.task_type_category)
        return TaskTransitionController(task, None)


def translated(transition):
    return translate(transition, context=getRequest(), domain='plone')


class TestCancelledOpenGuard(IntegrationTestCase):
    transition = 'task-transition-cancelled-open'

    def test_only_available_when_user_is_issuer(self):
        self.login(self.regular_user)
        self.set_workflow_state('task-state-cancelled', self.task)

        # not issuer
        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.task))

        # issuer
        self.login(self.dossier_responsible)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.task))

    @browsing
    def test_issuing_inbox_group_has_agency_permission(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.set_workflow_state('task-state-cancelled', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    @browsing
    def test_administrator_has_agency_permission(self, browser):
        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-cancelled', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    @browsing
    def test_limited_admin_has_agency_permission(self, browser):
        self.login(self.limited_admin, browser=browser)
        self.set_workflow_state('task-state-cancelled', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    def test_not_available_if_dossier_is_closed(self):
        self.login(self.administrator)

        self.set_workflow_state('task-state-cancelled', self.task)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.task))

        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.task))

    def test_not_available_on_subtasks_if_dossier_is_closed(self):
        self.login(self.dossier_responsible)

        self.set_workflow_state('task-state-cancelled', self.subtask)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.subtask))

        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.subtask))


class TestOpenCancelledGuard(IntegrationTestCase):
    transition = 'task-transition-open-cancelled'

    def test_only_available_when_user_is_issuer(self):
        self.login(self.regular_user)
        self.set_workflow_state('task-state-open', self.task)

        # not issuer
        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.task))

        # issuer
        self.login(self.dossier_responsible)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.task))

    def test_is_not_available_on_subtasks_from_tasktemplatefolder(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-open', self.subtask)
        alsoProvides(self.subtask, IFromTasktemplateGenerated)

        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.subtask))

    @browsing
    def test_administrator_has_agency_permission(self, browser):
        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    @browsing
    def test_limited_admin_has_agency_permission(self, browser):
        self.login(self.limited_admin, browser=browser)
        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    @browsing
    def test_issuing_inbox_group_has_agency_permission(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)


class TestInProgressCancelledGuard(IntegrationTestCase):
    transition = 'task-transition-in-progress-cancelled'

    def test_only_available_when_user_is_issuer(self):
        self.login(self.regular_user)
        self.set_workflow_state('task-state-in-progress', self.task)

        # not issuer
        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.task))

        # issuer
        self.login(self.dossier_responsible)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.task))

    @browsing
    def test_administrator_has_agency_permission(self, browser):
        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-in-progress', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    @browsing
    def test_limited_admin_has_agency_permission(self, browser):
        self.login(self.limited_admin, browser=browser)
        self.set_workflow_state('task-state-in-progress', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    @browsing
    def test_issuing_inbox_group_has_agency_permission(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.set_workflow_state('task-state-in-progress', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn(translated(self.transition), browser.css('.agency_buttons a').text)
        self.assertNotIn(
            translated(self.transition), browser.css('.regular_buttons a').text)

    def test_only_available_for_tasktemplate_process_main_tasks(self):
        self.login(self.regular_user)
        self.set_workflow_state('task-state-in-progress', self.task)
        self.set_workflow_state('task-state-in-progress', self.subtask)

        alsoProvides(self.task, IFromTasktemplateGenerated)
        alsoProvides(self.subtask, IFromTasktemplateGenerated)

        self.assertIn(self.transition, self.get_workflow_transitions_for(self.task))
        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.subtask))

    @browsing
    def test_not_available_for_predecessor_and_successor(self, browser):
        self.login(self.dossier_responsible, browser)
        predecessor = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=self.dossier_responsible.id,
                    responsible=self.regular_user.id,
                    responsible_client='rk',
                    task_type='correction')
            .in_state('task-state-open')
            .titled(u'Inquiry from a concerned citizen'))

        sql_task = predecessor.get_sql_object()
        with self.login(self.regular_user):
            successor = accept_task_with_successor(
                self.dossier,
                'plone:%s' % sql_task.int_id,
                u'I accept this task',
            )

        self.assertNotIn(self.transition, self.get_workflow_transitions_for(predecessor))
        self.assertNotIn(self.transition, self.get_workflow_transitions_for(successor))

    @browsing
    def test_available_for_forwarding_successor(self, browser):
        self.login(self.secretariat_user, browser)
        forwarding_successor = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=self.secretariat_user.id,
                    responsible=self.regular_user.id,
                    responsible_client='rk',
                    task_type='correction')
            .in_state('task-state-in-progress').successor_from(self.inbox_forwarding))
        self.assertIn(self.transition, self.get_workflow_transitions_for(forwarding_successor))


class TestInProgressResolvedGuard(BaseTransitionGuardTests):
    transition = 'task-transition-in-progress-resolved'

    def test_never_available_for_unidirectional_by_value(self):
        checker = FakeChecker(is_administrator=True)
        self.task_type_category = 'unidirectional_by_value'
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_default_allowed(self):
        checker = FakeChecker(is_responsible=True,
                              all_subtasks_finished=True,
                              has_successors=False)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_is_allowed_for_predecessor_when_its_an_remote_request(self):
        args = dict(is_responsible=True,
                    all_subtasks_finished=True,
                    has_successors=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, FakeChecker(**args)))

        args['is_remote_request'] = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, FakeChecker(**args)))

    def test_subtasks_has_to_be_finished(self):
        checker = FakeChecker(is_responsible=True,
                              all_subtasks_finished=False,
                              has_successors=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_agency_fallback_for_responsible_orgunit_agency(self):
        checker = FakeChecker(is_responsible=False,
                              all_subtasks_finished=True,
                              has_successors=False,
                              responsible_agency=True)

        self.assertFalse(
            self.controller._is_transition_possible(
                self.transition, False, checker))

        self.assertTrue(
            self.controller._is_transition_possible(
                self.transition, True, checker))

    def test_agency_fallback_for_administrator(self):
        checker = FakeChecker(is_responsible=False,
                              all_subtasks_finished=True,
                              has_successors=False,
                              responsible_agency=False,
                              is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestSkipRejectedGuard(IntegrationTestCase):
    transition = 'task-transition-rejected-skipped'

    def test_available_when_user_is_issuer_or_admin(self):
        self.login(self.regular_user)
        self.set_workflow_state('task-state-rejected', self.seq_subtask_1)

        # not issuer
        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.seq_subtask_1))

        # issuer
        self.login(self.secretariat_user)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.seq_subtask_1))

        # limited admin
        self.login(self.limited_admin)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.seq_subtask_1))

        # administrator
        self.login(self.administrator)
        self.assertIn(
            self.transition, self.get_workflow_transitions_for(self.seq_subtask_1))

    def test_not_available_when_task_is_not_part_of_a_task_sequence(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-rejected', self.task)

        self.assertNotIn(
            self.transition, self.get_workflow_transitions_for(self.task))


class TestInProgressClosed(BaseTransitionGuardTests):

    transition = 'task-transition-in-progress-tested-and-closed'
    task_type_category = 'unidirectional_by_value'

    def test_never_available_for_bidirectional_tasks(self):
        self.task_type_category = 'directional_by_value'
        checker = FakeChecker(is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_default_allowed(self):
        checker = FakeChecker(is_responsible=True,
                              all_subtasks_finished=True,
                              has_successors=False)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_is_allowed_for_predecessor_when_its_an_remote_request(self):
        args = dict(is_responsible=True,
                    all_subtasks_finished=True,
                    has_successors=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, FakeChecker(**args)))

        args['is_remote_request'] = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, FakeChecker(**args)))

    def test_subtas_has_to_be_finished(self):
        checker = FakeChecker(is_responsible=True,
                              all_subtasks_finished=False,
                              has_successors=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_subtasks_has_to_be_finished(self):
        checker = FakeChecker(is_responsible=True,
                              all_subtasks_finished=False,
                              has_successors=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_agency_fallback_for_responsible_agency(self):
        checker = FakeChecker(is_responsible=False,
                              all_subtasks_finished=True,
                              has_successors=False,
                              responsible_agency=True)

        self.assertFalse(
            self.controller._is_transition_possible(
                self.transition, False, checker))

        self.assertTrue(
            self.controller._is_transition_possible(
                self.transition, True, checker))

    def test_agency_fallback_for_administrator(self):
        checker = FakeChecker(is_responsible=False,
                              all_subtasks_finished=True,
                              has_successors=False,
                              responsible_agency=False,
                              is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestOpenInProgress(BaseTransitionGuardTests):

    transition = 'task-transition-open-in-progress'
    task_type_category = 'bidirectional_by_value'

    def test_never_available_for_unidirectional_by_refernce_tasks(self):
        self.task_type_category = 'unidirectional_by_reference'
        checker = FakeChecker(is_responsible=True, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_is_available_for_responsible(self):
        checker = FakeChecker(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_agency_fallback_for_responsible(self):
        checker = FakeChecker(is_responsible=False,
                              responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_agency_fallback_for_administrators(self):
        checker = FakeChecker(is_responsible=False,
                              responsible_agency=False,
                              is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestOpenRejected(BaseTransitionGuardTests):
    transition = 'task-transition-open-rejected'

    def test_is_available_for_responsible(self):
        checker = FakeChecker(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_agency_fallback_for_responsible(self):
        checker = FakeChecker(is_responsible=False,
                              responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_agency_fallback_for_administrators(self):
        checker = FakeChecker(is_responsible=False,
                              responsible_agency=False,
                              is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestOpenResolved(BaseTransitionGuardTests):
    transition = 'task-transition-open-resolved'
    task_type_category = 'bidirectional_by_value'

    def test_only_available_for_bidrectional_tasks(self):
        checker = FakeChecker(is_responsible=True, is_administrator=True)

        self.task_type_category = 'unidirectional_by_reference'
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.task_type_category = 'unidirectional_by_value'
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_is_available_for_responsible(self):
        checker = FakeChecker(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_responsible_agency(self):
        checker = FakeChecker(is_responsible=False,
                              responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_agency_fallback_for_administrators(self):
        checker = FakeChecker(is_responsible=False,
                              responsible_agency=False,
                              is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestOpenClosed(BaseTransitionGuardTests):
    transition = 'task-transition-open-tested-and-closed'

    def test_available_for_responsible_for_unidirectional_by_reference_tasks(self):
        self.task_type_category = 'unidirectional_by_reference'
        checker = FakeChecker(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_responsible_agency_for_unidirectional_by_reference_tasks(self):
        self.task_type_category = 'unidirectional_by_reference'
        checker = FakeChecker(
            is_responsible=False, responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_agency_fallback_for_administrator_on_unidirectional_by_reference_tasks(self):
        self.task_type_category = 'unidirectional_by_reference'
        checker = FakeChecker(
            is_responsible=False, responsible_agency=False, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_available_for_issuer_for_bidirectional_tasks(self):
        checker = FakeChecker(is_issuer=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_issuer_agency_for_bidirectional_tasks(self):
        checker = FakeChecker(is_issuer=False, issuing_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_agency_fallback_for_administrators_on_bidirectional_tasks(self):
        checker = FakeChecker(
            is_issuer=False, issuing_agency=False, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_available_for_issuer_for_unidirectional_by_value_tasks(self):
        self.task_type_category = 'unidirectional_by_value'
        checker = FakeChecker(is_issuer=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_available_for_responsible_for_unidirectional_by_value_tasks(self):
        self.task_type_category = 'unidirectional_by_value'
        checker = FakeChecker(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_issuer_agency_for_unidirectional_by_value_tasks(self):
        self.task_type_category = 'unidirectional_by_value'
        checker = FakeChecker(issuing_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_responsible_agency_for_unidirectional_by_value_tasks(self):
        self.task_type_category = 'unidirectional_by_value'
        checker = FakeChecker(responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestReassign(IntegrationTestCase):
    transition = 'task-transition-reassign'

    def test_guarded_by_modify_portal_content(self):
        self.login(self.regular_user)
        self.assertIn(self.transition, self.get_workflow_transitions_for(self.task))

        RoleAssignmentManager(self.portal).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
        )
        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
        )

        self.login(self.reader_user)
        self.assertNotIn(self.transition, self.get_workflow_transitions_for(self.task))

    def test_editor_can_only_reassign_pending_tasks(self):
        self.login(self.regular_user)
        RoleAssignmentManager(self.task).add_or_update_assignment(
            SharingRoleAssignment(self.regular_user.getId(), ['Editor']),
        )
        allowed_states = ['task-state-in-progress', 'task-state-open',
                          'task-state-planned', 'task-state-resolved']
        disallowed_states = ['task-state-rejected', 'task-state-tested-and-closed',
                            'task-state-skipped', 'task-state-cancelled']

        for state in allowed_states:
            self.set_workflow_state(state, self.task)
            self.assertIn(self.transition, self.get_workflow_transitions_for(self.task))

        for state in disallowed_states:
            self.set_workflow_state(state, self.task)
            self.assertNotIn(self.transition, self.get_workflow_transitions_for(self.task))

    def test_administrator_can_reassign_rejected_tasks(self):
        self.login(self.administrator)
        self.set_workflow_state('task-state-rejected', self.task)
        self.assertIn(self.transition, self.get_workflow_transitions_for(self.task))

    def test_limited_admin_can_reassign_rejected_tasks(self):
        self.login(self.limited_admin)
        self.set_workflow_state('task-state-rejected', self.task)
        self.assertIn(self.transition, self.get_workflow_transitions_for(self.task))


class TestDelegate(IntegrationTestCase):
    transition = 'task-transition-delegate'

    def test_guarded_by_modify_portal_content(self):
        self.login(self.regular_user)
        self.assertIn(self.transition, self.get_workflow_transitions_for(self.task))

        RoleAssignmentManager(self.portal).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
        )
        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
        )

        self.login(self.reader_user)
        self.assertNotIn(self.transition, self.get_workflow_transitions_for(self.task))


class TestRejectedOpen(BaseTransitionGuardTests):
    transition = 'task-transition-rejected-open'

    def test_is_available_for_issuer(self):
        checker = FakeChecker()
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        checker = FakeChecker(is_issuer=True)
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_agency_fallback_for_administrators(self):
        checker = FakeChecker(is_issuer=False, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestResolvedClosed(BaseTransitionGuardTests):
    transition = 'task-transition-resolved-tested-and-closed'

    def test_is_available_for_issuer(self):
        checker = FakeChecker(is_issuer=False)
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        checker = FakeChecker(is_issuer=True)
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_issuing_agency(self):
        checker = FakeChecker(is_issuer=False, issuing_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_agency_fallback_for_administrators(self):
        checker = FakeChecker(
            is_issuer=False, issuing_agency=False, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class ResolvedInProgress(BaseTransitionGuardTests):
    transition = 'task-transition-resolved-in-progress'

    def test_available_for_issuer(self):
        checker = FakeChecker(is_issuer=True)
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_available_for_responsible(self):
        checker = FakeChecker(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_responsible_agency(self):
        checker = FakeChecker(
            is_issuer=False, is_responsible=False, responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))

    def test_agency_fallback_for_administrators(self):
        checker = FakeChecker(
            is_issuer=False, is_responsible=False,
            responsible_agency=False, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class ClosedInProgress(BaseTransitionGuardTests):
    transition = 'task-transition-tested-and-closed-in-progress'

    def test_available_for_admin(self):
        checker = FakeChecker(
            is_administrator=True, parent_task_is_in_progress=True)
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_not_available_for_task_with_tasktype_information(self):
        self.task_type_category = 'unidirectional_by_reference'

        checker = FakeChecker(
            is_administrator=True, parent_task_is_in_progress=True)
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_not_available_if_parent_task_is_not_in_progress(self):
        checker = FakeChecker(
            is_administrator=True, parent_task_is_in_progress=False)
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_not_available_for_responsible_or_issuer(self):
        checker = FakeChecker(
            is_responsible=True, is_issuer=True,
            is_administrator=False, parent_task_is_in_progress=True)
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
