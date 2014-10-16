from opengever.inbox.browser.transitioncontroller import ForwardingTransitionController
from opengever.task.tests.test_transitioncontroller import BaseTransitionGuardTests
from opengever.task.tests.test_transitioncontroller import FakeConditions
from opengever.task.tests.test_transitioncontroller import FakeTask


class InboxBaseTransitionGuardTests(BaseTransitionGuardTests):
    task_type_category = 'forwarding-task-type'

    @property
    def controller(self):
        task = FakeTask(self.task_type_category)
        return ForwardingTransitionController(task, None)


class TestAcceptGuard(InboxBaseTransitionGuardTests):

    transition = 'forwarding-transition-accept'

    def test_is_available_for_responsible(self):
        conditions = FakeConditions()

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_responsible = True

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_is_not_available_for_admin_unit_intern_forwardings(self):
        conditions = FakeConditions(current_admin_unit_assigned=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

    def test_is_available_for_admin_unit_intern_forwardings_during_succesor_process(self):
        conditions = FakeConditions(
            current_admin_unit_assigned=True,
            successor_process=True,
            is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))


class TestRefuseGuard(TestAcceptGuard):
    transition = 'forwarding-transition-refuse'


class TestAssignToDossierGuard(InboxBaseTransitionGuardTests):
    transition = 'forwarding-transition-assign-to-dossier'

    def test_is_only_available_for_responsible_of_admin_unit_intern_forwardings(self):
        conditions = FakeConditions()
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_responsible = True
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_assigned_to_current_admin_unit = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, conditions))

        conditions.is_responsible = False
        conditions.is_responsible_orgunit_agency_member = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, conditions))


class TestReassignGuard(TestAssignToDossierGuard):
    transition = 'forwarding-transition-reassign'


class TestCloseGuard(TestAssignToDossierGuard):
    transition = 'forwarding-transition-close'


class TestReassignRefuseGuard(TestAssignToDossierGuard):
    transition = 'forwarding-transition-reassign-refused'
