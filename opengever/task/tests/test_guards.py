from ftw.testing import MockTestCase
from mocker import ANY
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.browser.transitioncontroller import ITaskTransitionController
from opengever.task.browser.transitioncontroller import TaskTransitionController
from opengever.task.task import ITask
from zope.interface import Interface
from zope.interface.verify import verifyClass

class TestTaskTransitionController(MockTestCase):

    def test_verify_class(self):
        self.assertTrue(
            verifyClass(ITaskTransitionController,
                        TaskTransitionController))

    def test_is_issuer(self):
        task1 = self.mocker.mock()
        self.expect(task1.issuer).result('hugo.boss')
        task2 = self.mocker.mock()
        self.expect(task2.issuer).result('james.bond')

        plone_portal_state = self.stub()
        self.expect(
            plone_portal_state(ANY, ANY)).result(plone_portal_state)
        self.expect(plone_portal_state.member().id).result('hugo.boss')
        self.mock_adapter(
            plone_portal_state, ITask, [Interface, Interface], 'plone_portal_state')

        self.replay()

        self.assertTrue(TaskTransitionController(task1, {})._is_issuer())
        self.assertFalse(TaskTransitionController(task2, {})._is_issuer())

    def test_is_responsible(self):
        task1 = self.mocker.mock()
        self.expect(task1.responsible).result('hugo.boss')
        task2 = self.mocker.mock()
        self.expect(task2.responsible).result('james.bond')

        plone_portal_state = self.stub()
        self.expect(
            plone_portal_state(ANY, ANY)).result(plone_portal_state)
        self.expect(plone_portal_state.member().id).result('james.bond')
        self.mock_adapter(
            plone_portal_state, ITask, [Interface, Interface], 'plone_portal_state')

        self.replay()

        self.assertTrue(TaskTransitionController(task2, {})._is_responsible())
        self.assertFalse(TaskTransitionController(task1, {})._is_responsible())

    def test_is_responsible_or_inbox_group_user(self):
        task1 = self.stub()
        self.expect(task1.responsible).result('hugo.boss')

        plone_portal_state = self.stub()
        self.expect(
            plone_portal_state(ANY, ANY)).result(plone_portal_state)
        self.expect(plone_portal_state.member().id).result('hugo.boss')
        self.mock_adapter(
            plone_portal_state, ITask, [Interface, Interface], 'plone_portal_state')

        contact_info = self.mocker.mock()
        self.mock_utility(contact_info, IContactInformation, name=u"")
        with self.mocker.order():
            self.expect(contact_info.is_user_in_inbox_group()).result(False).count(0, None)
            self.expect(contact_info.is_user_in_inbox_group()).result(True).count(0, None)

        self.replay()

        self.assertTrue(TaskTransitionController(
                task1, {})._is_responsible_or_inbox_group_user())
        self.assertTrue(TaskTransitionController(
                task1, {})._is_responsible_or_inbox_group_user())

    def test_type_category_methods(self):
        task1 = self.mocker.mock()
        task2 = self.mocker.mock()
        task3 = self.mocker.mock()
        task4 = self.mocker.mock()

        self.expect(task1.task_type_category).result(
            'unidirectional_by_reference').count(0, None)
        self.expect(task2.task_type_category).result(
            'unidirectional_by_value').count(0, None)
        self.expect(task3.task_type_category).result(
            'bidirectional_by_value').count(0, None)
        self.expect(task4.task_type_category).result(
            'bidirectional_by_reference').count(0, None)

        self.replay()

        self.assertFalse(TaskTransitionController(task1, {})._is_unidirectional_by_value())
        self.assertTrue(TaskTransitionController(task2, {})._is_unidirectional_by_value())

        self.assertTrue(TaskTransitionController(task1, {})._is_unidirectional_by_reference())
        self.assertFalse(TaskTransitionController(task2, {})._is_unidirectional_by_reference())

        self.assertFalse(TaskTransitionController(task1, {})._is_bidirectional())
        self.assertFalse(TaskTransitionController(task2, {})._is_bidirectional())
        self.assertTrue(TaskTransitionController(task3, {})._is_bidirectional())
        self.assertTrue(TaskTransitionController(task4, {})._is_bidirectional())


    def test_is_cancelled_to_open_possible(self):
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        self.assertFalse(controller.is_cancelled_to_open_possible())
        self.assertTrue(controller.is_cancelled_to_open_possible())


    def test_is_progress_to_resolved_possible(self):
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            # Task 1
            self.expect(controller_mock._is_responsible()).result(False)
            self.expect(controller_mock._is_inbox_group_user()).result(False)

            self.expect(controller_mock._is_responsible()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(False)

            self.expect(controller_mock._is_responsible()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._is_unidirectional_by_value()).result(True)

            self.expect(controller_mock._is_responsible()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._is_unidirectional_by_value()).result(False)

            self.expect(controller_mock._is_responsible()).result(False)
            self.expect(controller_mock._is_inbox_group_user()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._is_unidirectional_by_value()).result(False)


        self.replay()
        self.assertFalse(controller.is_progress_to_resolved_possible())
        self.assertFalse(controller.is_progress_to_resolved_possible())
        self.assertFalse(controller.is_progress_to_resolved_possible())
        self.assertTrue(controller.is_progress_to_resolved_possible())
        self.assertTrue(controller.is_progress_to_resolved_possible())

    def test_is_progress_to_closed_possible(self):
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            self.expect(controller_mock._is_unidirectional_by_value()).result(False)

            self.expect(controller_mock._is_unidirectional_by_value()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(False)

            self.expect(controller_mock._is_unidirectional_by_value()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(True)

        self.replay()
        self.assertFalse(controller.is_progress_to_closed_possible())
        self.assertFalse(controller.is_progress_to_closed_possible())
        self.assertTrue(controller.is_progress_to_closed_possible())

    def test_is_cancel_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        self.assertFalse(controller.is_cancel_possible())
        self.assertTrue(controller.is_cancel_possible())

    def test_is_open_to_progress_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_unidirectional_by_reference()).result(True)

            self.expect(controller_mock._is_unidirectional_by_reference()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)
            self.expect(task.issuer).result('james.bond')
            self.expect(task.responsible).result('hugo.boss')

            self.expect(controller_mock._is_unidirectional_by_reference()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)
            self.expect(task.issuer).result('hugo.boss')
            self.expect(task.responsible).result('hugo.boss')

            self.expect(controller_mock._is_unidirectional_by_reference()).result(False)
            self.expect(controller_mock._is_issuer()).result(False)

        self.replay()
        self.assertFalse(controller.is_open_to_progress_possible())
        self.assertFalse(controller.is_open_to_progress_possible())
        self.assertTrue(controller.is_open_to_progress_possible())
        self.assertTrue(controller.is_open_to_progress_possible())

    def test_is_reject_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_responsible()).result(False)
            self.expect(controller_mock._is_responsible()).result(True)

        self.replay()
        self.assertFalse(controller.is_reject_possible())
        self.assertTrue(controller.is_reject_possible())

    def test_is_open_to_resolved_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_substasks_closed()).result(False)

            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._is_bidirectional()).result(False)

            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._is_bidirectional()).result(True)
            self.expect(controller_mock._is_issuer()).result(True)
            self.expect(task.issuer).result('james.bond')
            self.expect(task.responsible).result('hugo.boss')

            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._is_bidirectional()).result(True)
            self.expect(controller_mock._is_issuer()).result(True)
            self.expect(task.issuer).result('james.bond')
            self.expect(task.responsible).result('james.bond')

            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._is_bidirectional()).result(True)
            self.expect(controller_mock._is_issuer()).result(False)

        self.replay()
        self.assertFalse(controller.is_open_to_resolved_possible())
        self.assertFalse(controller.is_open_to_resolved_possible())
        self.assertFalse(controller.is_open_to_resolved_possible())
        self.assertTrue(controller.is_open_to_resolved_possible())
        self.assertTrue(controller.is_open_to_resolved_possible())

    def test_is_open_to_closed_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_unidirectional_by_reference()).result(False)

            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_unidirectional_by_reference()).result(True)

            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        self.assertFalse(controller.is_open_to_closed_possible())
        self.assertTrue(controller.is_open_to_closed_possible())
        self.assertTrue(controller.is_open_to_closed_possible())

    def test_is_rejected_to_open_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        self.assertFalse(controller.is_rejected_to_open_possible())
        self.assertTrue(controller.is_rejected_to_open_possible())

    def test_is_resolved_to_closed_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        self.assertFalse(controller.is_resolved_to_closed_possible())
        self.assertTrue(controller.is_resolved_to_closed_possible())

    def _create_task_controller(self):
        task1 = self.mocker.mock()
        controller = TaskTransitionController(task1, {})
        controller_mock = self.mocker.patch(controller)

        return controller, controller_mock, task1
