from ftw.testing import MockTestCase
from mocker import ANY
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.browser.transitioncontroller import \
    ITaskTransitionController, TaskTransitionController
from opengever.task.interfaces import ISuccessorTaskController
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
        self.mock_adapter(plone_portal_state,
                          ITask, [Interface, Interface], 'plone_portal_state')

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
        self.mock_adapter(plone_portal_state,
                          ITask, [Interface, Interface], 'plone_portal_state')

        self.replay()

        self.assertTrue(TaskTransitionController(task2, {})._is_responsible())
        self.assertFalse(TaskTransitionController(task1, {})._is_responsible())

    def test_has_successors(self):
        task1 = self.mocker.mock()

        successor_task_controller = self.stub()
        self.expect(
            successor_task_controller(ANY)).result(successor_task_controller)

        with self.mocker.order():
            self.expect(successor_task_controller.get_successors()).result(
                None)
            self.expect(successor_task_controller.get_successors()).result(
                [])
            self.expect(successor_task_controller.get_successors()).result(
                [object(), object])
        self.mock_adapter(
            successor_task_controller, ISuccessorTaskController, [Interface])

        self.replay()

        self.assertFalse(TaskTransitionController(task1, {})._has_successors())
        self.assertFalse(TaskTransitionController(task1, {})._has_successors())
        self.assertTrue(TaskTransitionController(task1, {})._has_successors())

    def test_is_remote_request(self):
        task1 = self.mocker.mock()
        mock_request = self.mocker.mock()
        successor_task_controller = self.stub()
        self.expect(
            successor_task_controller(ANY)).result(successor_task_controller)
        self.mock_adapter(
            successor_task_controller, ISuccessorTaskController, [Interface])

        with self.mocker.order():
            self.expect(mock_request.get_header('X-OGDS-CID', None)).result(None)
            self.expect(mock_request.get_header('X-OGDS-CID', None)).result('TEST_CLIENT_ID')

        self.replay()
        self.assertFalse(TaskTransitionController(task1, mock_request)._is_remote_request())
        self.assertTrue(TaskTransitionController(task1, mock_request)._is_remote_request())

    def test_is_responsible_or_inbox_group_user(self):
        task1 = self.stub()
        self.expect(task1.responsible).result('hugo.boss')

        plone_portal_state = self.stub()
        self.expect(
            plone_portal_state(ANY, ANY)).result(plone_portal_state)
        self.expect(plone_portal_state.member().id).result('hugo.boss')
        self.mock_adapter(plone_portal_state,
                          ITask, [Interface, Interface], 'plone_portal_state')

        contact_info = self.mocker.mock()
        self.mock_utility(contact_info, IContactInformation, name=u"")
        with self.mocker.order():
            self.expect(contact_info.is_user_in_inbox_group()).result(
                False).count(0, None)
            self.expect(contact_info.is_user_in_inbox_group()).result(
                True).count(0, None)

        self.replay()

        self.assertTrue(TaskTransitionController(
                task1, {})._is_responsible_or_inbox_group_user())
        self.assertTrue(TaskTransitionController(
                task1, {})._is_responsible_or_inbox_group_user())

    def test_is_cancelled_to_open_possible(self):
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-cancelled-open'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_progress_to_resolved_possible(self):
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            # Task 1
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(controller_mock._is_responsible()).result(False)
            self.expect(controller_mock._is_inbox_group_user()).result(False)

            # Task 2
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')

            # Task 3
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(controller_mock._is_responsible()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(False)

            # Task 4
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(controller_mock._is_responsible()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._has_successors()).result(True)
            self.expect(controller_mock._is_remote_request()).result(False)

            # # Task 5
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(controller_mock._is_responsible()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._has_successors()).result(True)
            self.expect(controller_mock._is_remote_request()).result(True)

            # # Task 6
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(controller_mock._is_responsible()).result(True)
            self.expect(controller_mock._is_substasks_closed()).result(True)
            self.expect(controller_mock._has_successors()).result(False)

        self.replay()
        transition = 'task-transition-in-progress-resolved'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_progress_to_closed_possible(self):
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            #task1
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')

            #task2
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(False)

            #task3
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(True)
            self.expect(
                controller_mock._is_substasks_closed()).result(False)

            #task4
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(True)
            self.expect(
                controller_mock._is_substasks_closed()).result(True)
            self.expect(
                controller_mock._has_successors()).result(True)
            self.expect(controller_mock._is_remote_request()).result(False)

            #task5
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(True)
            self.expect(
                controller_mock._is_substasks_closed()).result(True)
            self.expect(
                controller_mock._has_successors()).result(True)
            self.expect(controller_mock._is_remote_request()).result(True)

            #task6
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(True)
            self.expect(
                controller_mock._is_substasks_closed()).result(True)
            self.expect(
                controller_mock._has_successors()).result(True)
            self.expect(controller_mock._is_remote_request()).result(True)

        self.replay()

        transition = 'task-transition-in-progress-tested-and-closed'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_cancel_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-open-cancelled'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_open_to_progress_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            #task1
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')

            #task2
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')

            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)

            #task3
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)

        self.replay()
        transition = 'task-transition-open-in-progress'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_reject_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(False)
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(True)

        self.replay()
        transition = 'task-transition-open-rejected'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_open_to_resolved_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            #task1
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')

            #task2
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')

            #task3
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)
            #task4
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)

        self.replay()
        transition = 'task-transition-open-resolved'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_open_to_closed_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            # task1
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)

            # task2
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)

            # task3
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(controller_mock._is_issuer()).result(False)

            # task4
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-open-tested-and-closed'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_rejected_to_open_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-rejected-open'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_resolved_to_closed_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-resolved-tested-and-closed'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_is_resolved_to_progress_possible(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-resolved-in-progress'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))


    def _create_task_controller(self):
        task1 = self.mocker.mock()
        controller = TaskTransitionController(task1, {})
        controller_mock = self.mocker.patch(controller)

        return controller, controller_mock, task1
