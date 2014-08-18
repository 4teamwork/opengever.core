from opengever.task.browser.transitioncontroller import TaskTransitionController
import unittest2


class FakeConditions(object):

    def __init__(self, is_issuer=False, is_responsible=False,
                 all_subtasks_finished=False, has_successors=False,
                 is_remote_request=False,
                 issuing_agency=False, responsible_agency=False,
                 successor_process=False, current_admin_unit_assigned=False):

        self.is_issuer = is_issuer
        self.is_responsible = is_responsible
        self.is_responsible_orgunit_agency_member = responsible_agency
        self.all_subtasks_finished = all_subtasks_finished
        self.has_successors = has_successors
        self.is_remote_request = is_remote_request
        self.is_issuing_orgunit_agency_member = issuing_agency
        self.is_responsible_orgunit_agency_member = responsible_agency
        self.is_assigned_to_current_admin_unit = current_admin_unit_assigned
        self.is_successor_process = successor_process


class FakeTask(object):
    def __init__(self, category):
        self._category = category

    @property
    def task_type_category(self):
        return self._category


class BaseTransitionGuardTests(unittest2.TestCase):
    task_type_category = 'bidirectional_by_value'

    @property
    def controller(self):
        task = FakeTask(self.task_type_category)
        return TaskTransitionController(task, None)


class TestCancelledOpenGuard(BaseTransitionGuardTests):
    transition = 'task-transition-cancelled-open'

    def test_only_available_when_user_is_issuer(self):
        conditions = FakeConditions(is_issuer=True)

        self.assertTrue(
            self.controller._is_transition_possible(
                self.transition, False, conditions))

        conditions = FakeConditions(is_issuer=False)
        self.assertFalse(
            self.controller._is_transition_possible(
                self.transition, False, conditions))

    def test_issuing_inbox_group_has_agency_permission(self):
        conditions = FakeConditions(is_issuer=False, issuing_agency=True)
        self.assertTrue(
            self.controller._is_transition_possible(
                self.transition, True, conditions))


class TestOpenCancelledGuard(BaseTransitionGuardTests):
    transition = 'task-transition-open-cancelled'

    def test_only_available_when_user_is_issuer(self):
        conditions = FakeConditions(is_issuer=True)

        self.assertTrue(
            self.controller._is_transition_possible(
                self.transition, False, conditions))

        conditions = FakeConditions(is_issuer=False)
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_issuing_inbox_group_has_agency_permission(self):
        conditions = FakeConditions(is_issuer=False, issuing_agency=True)
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class TestInProgressResolvedGuard(BaseTransitionGuardTests):
    transition = 'task-transition-in-progress-resolved'

    def test_never_available_for_unidirectional_by_value(self):
        conditions = FakeConditions()
        self.task_type_category = 'unidirectional_by_value'
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_default_allowed(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=True,
                                    has_successors=False)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_is_allowed_for_predecessor_when_its_an_remote_request(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=True,
                                    has_successors=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_remote_request = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_subtas_has_to_be_finished(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=False,
                                    has_successors=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_subtasks_has_to_be_finished(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=False,
                                    has_successors=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_agency_fallback_for_responsible(self):
        conditions = FakeConditions(is_responsible=False,
                                    all_subtasks_finished=True,
                                    has_successors=False,
                                    responsible_agency=True)

        self.assertFalse(
            self.controller._is_transition_possible(
                self.transition, False, conditions))

        self.assertTrue(
            self.controller._is_transition_possible(
                self.transition, True, conditions))


class TestInProgressClosed(BaseTransitionGuardTests):

    transition = 'task-transition-in-progress-tested-and-closed'
    task_type_category = 'unidirectional_by_value'

    def test_never_available_for_bidirectional_tasks(self):
        task_type_category = 'directional_by_value'
        conditions = FakeConditions()

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, True, conditions))

    def test_default_allowed(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=True,
                                    has_successors=False)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_is_allowed_for_predecessor_when_its_an_remote_request(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=True,
                                    has_successors=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_remote_request = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_subtas_has_to_be_finished(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=False,
                                    has_successors=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_subtasks_has_to_be_finished(self):
        conditions = FakeConditions(is_responsible=True,
                                    all_subtasks_finished=False,
                                    has_successors=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_agency_fallback_for_responsible(self):
        conditions = FakeConditions(is_responsible=False,
                                    all_subtasks_finished=True,
                                    has_successors=False,
                                    responsible_agency=True)

        self.assertFalse(
            self.controller._is_transition_possible(
                self.transition, False, conditions))

        self.assertTrue(
            self.controller._is_transition_possible(
                self.transition, True, conditions))


class TestOpenInProgress(BaseTransitionGuardTests):

    transition = 'task-transition-open-in-progress'
    task_type_category = 'bidirectional_by_value'

    def test_never_available_for_unidirectional_by_refernce_tasks(self):
        self.task_type_category = 'unidirectional_by_reference'
        conditions = FakeConditions(is_responsible=True)

    def test_is_available_for_responsible(self):
        conditions = FakeConditions(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_agency_fallback_for_responsible(self):
        conditions = FakeConditions(is_responsible=False,
                                    responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class TestOpenRejected(BaseTransitionGuardTests):
    transition = 'task-transition-open-rejected'

    def test_is_available_for_responsible(self):
        conditions = FakeConditions(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_agency_fallback_for_responsible(self):
        conditions = FakeConditions(is_responsible=False,
                                    responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class TestOpenResolved(BaseTransitionGuardTests):
    transition = 'task-transition-open-resolved'
    task_type_category = 'bidirectional_by_value'

    def test_only_available_for_bidrectional_tasks(self):
        conditions = FakeConditions(is_responsible=True)

        self.task_type_category = 'unidirectional_by_reference'
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.task_type_category = 'unidirectional_by_value'
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_is_available_for_responsible(self):
        conditions = FakeConditions(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_responsible_agency(self):
        conditions = FakeConditions(is_responsible=False,
                                    responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class TestOpenClosed(BaseTransitionGuardTests):
    transition = 'task-transition-open-tested-and-closed'

    def test_available_for_responsible_for_unidirectional_by_reference_tasks(self):
        self.task_type_category = 'unidirectional_by_reference'
        conditions = FakeConditions(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_responsible_agency_for_unidirectional_by_reference_tasks(self):
        self.task_type_category = 'unidirectional_by_reference'

        conditions = FakeConditions(
            is_responsible=False, responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))

    def test_available_for_issuer_for_bidirectional_tasks(self):
        conditions = FakeConditions(is_issuer=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_issuer_agency_for_bidirectional_tasks(self):
        conditions = FakeConditions(is_issuer=False, issuing_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class TestReassign(BaseTransitionGuardTests):
    transition = 'task-transition-reassign'

    def test_has_no_guard(self):
        conditions = FakeConditions(is_issuer=False, issuing_agency=True)
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class TestRejectedOpen(BaseTransitionGuardTests):
    transition = 'task-transition-rejected-open'

    def test_is_available_for_issuer(self):
        conditions = FakeConditions()

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_issuer = True

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))


class TestResolvedClosed(BaseTransitionGuardTests):
    transition = 'task-transition-resolved-tested-and-closed'

    def test_is_available_for_issuer(self):
        conditions = FakeConditions(is_issuer=False)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_issuer = True

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_issuing_agency(self):
        conditions = FakeConditions(is_issuer=False, issuing_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class ResolvedInProgress(BaseTransitionGuardTests):
    transition = 'task-transition-resolved-in-progress'

    def test_available_for_issuer(self):
        conditions = FakeConditions(is_issuer=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_available_for_responsible(self):
        conditions = FakeConditions(is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_responsible_agency(self):
        conditions = FakeConditions(
            is_issuer=False, is_responsible=False, responsible_agency=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))
