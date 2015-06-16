from opengever.inbox.browser.transitioncontroller import ForwardingTransitionController
from opengever.task.tests.test_transitioncontroller import BaseTransitionGuardTests
from opengever.task.tests.test_transitioncontroller import FakeChecker
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
        checker = FakeChecker()
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

        checker = FakeChecker(is_responsible=True)
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_is_not_available_for_admin_unit_intern_forwardings(self):
        checker = FakeChecker(current_admin_unit_assigned=True,
                                    is_responsible=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_is_available_for_admin_unit_intern_forwardings_during_succesor_process(self):
        checker = FakeChecker(
            current_admin_unit_assigned=True,
            successor_process=True,
            is_responsible=True)

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, checker))

    def test_fallback_agency_for_administrators(self):
        checker = FakeChecker(current_admin_unit_assigned=False,
                                    is_responsible=False, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestRefuseGuard(TestAcceptGuard):
    transition = 'forwarding-transition-refuse'


class TestAssignToDossierGuard(InboxBaseTransitionGuardTests):
    transition = 'forwarding-transition-assign-to-dossier'

    def test_is_only_available_for_responsible_of_admin_unit_intern_forwardings(self):
        args = dict()
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, FakeChecker(**args)))

        args['is_responsible'] = True
        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, FakeChecker(**args)))

        args['current_admin_unit_assigned'] = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, False, FakeChecker(**args)))

        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, FakeChecker(**args)))

        args['is_responsible'] = False
        args['responsible_agency'] = True
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, FakeChecker(**args)))

    def test_fallback_agency_for_administrators(self):
        checker = FakeChecker(
            current_admin_unit_assigned=True, is_responsible=False,
            responsible_agency=False, is_administrator=True)

        self.assertFalse(self.controller._is_transition_possible(
            self.transition, False, checker))
        self.assertTrue(self.controller._is_transition_possible(
            self.transition, True, checker))


class TestReassignGuard(TestAssignToDossierGuard):
    transition = 'forwarding-transition-reassign'


class TestCloseGuard(TestAssignToDossierGuard):
    transition = 'forwarding-transition-close'


class TestReassignRefuseGuard(TestAssignToDossierGuard):
    transition = 'forwarding-transition-reassign-refused'
