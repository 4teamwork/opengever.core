from Products.CMFPlone.interfaces import IPloneSiteRoot
from ftw.testing import MockTestCase
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.registry.interfaces import IRegistry
from mocker import ANY
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.browser.transitioncontroller import \
    ITaskTransitionController, TaskTransitionController
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from xml.dom.minidom import parse
from zope.interface import Interface
from zope.app.component.hooks import setSite
from zope.interface import alsoProvides
from zope.component import getSiteManager
from zope.interface.verify import verifyClass
import os.path


class TestTaskTransitionController(MockTestCase):

    def setUp(self):
        # we need to have a site root for making the get_client_id cachecky
        # work.
        root = self.create_dummy(getSiteManager=getSiteManager,
                                 id='root')
        alsoProvides(root, IPloneSiteRoot)
        setSite(root)

    def test_verify_class(self):
        self.assertTrue(
            verifyClass(ITaskTransitionController,
                        TaskTransitionController))

    def test_transitions_in_defintion_use_controller(self):
        import opengever.task
        path = os.path.join(
            os.path.dirname(os.path.abspath(opengever.task.__file__)),
            'profiles', 'default', 'workflows', 'opengever_task_workflow',
            'definition.xml')
        self.assertTrue(os.path.isfile(path))

        doc = parse(path)

        for node in doc.getElementsByTagName('transition'):
            transition = node.getAttribute('transition_id')
            self.assertEqual(node.getAttribute('title'), transition)

            actions = node.getElementsByTagName('action')
            self.assertEqual(len(actions), 1)
            self.assertEqual(actions[0].firstChild.nodeValue, transition)
            self.assertEqual(
                actions[0].getAttribute('url'),
                '%(content_url)s/@@task_transition_controller?transition=' +\
                    transition)

            guard = node.getElementsByTagName('guard-expression')[0]
            self.assertEqual(
                guard.firstChild.nodeValue,
                "python: here.restrictedTraverse('@@task_transition_" + \
                    "controller').is_transition_possible('%s')" % transition)

    def test_is_administrator(self):
        task1 = self.stub()
        mock = self.stub()
        self.mock_tool(mock, 'portal_membership')
        self.expect(mock.getAuthenticatedMember()).result(mock)

        with self.mocker.order():
            self.expect(mock.has_role('Adminstrator')).result(0)
            self.expect(mock.has_role('Manager')).result(0)

            self.expect(mock.has_role('Adminstrator')).result(0)
            self.expect(mock.has_role('Manager')).result(1)

            self.expect(mock.has_role('Adminstrator')).result(1)

        self.replay()

        self.assertFalse(
            TaskTransitionController(task1, {})._is_administrator())
        self.assertTrue(
            TaskTransitionController(task1, {})._is_administrator())
        self.assertTrue(
            TaskTransitionController(task1, {})._is_administrator())

    def test_is_issuer(self):
        task1 = self.stub()
        self.expect(task1.issuer).result('hugo.boss')
        task2 = self.stub()
        self.expect(task2.issuer).result('james.bond')
        task3 = self.stub()
        self.expect(task3.issuer).result('inbox:client1')

        contact_info = self.mocker.mock()
        self.mock_utility(contact_info, IContactInformation, name=u"")
        self.expect(contact_info.is_inbox('hugo.boss')).result(False)
        self.expect(contact_info.is_inbox('james.bond')).result(False)
        self.expect(contact_info.is_inbox('inbox:client1')).result(True)
        self.expect(contact_info.get_group_of_inbox('inbox:client1')).result(
            'client1_inbox_group')
        self.expect(
            contact_info.is_group_member(
                'client1_inbox_group', 'hugo.boss')).result(True)

        plone_portal_state = self.stub()
        self.expect(
            plone_portal_state(ANY, ANY)).result(plone_portal_state)
        self.expect(plone_portal_state.member().id).result('hugo.boss')
        self.mock_adapter(plone_portal_state,
                          ITask, [Interface, Interface], 'plone_portal_state')

        self.replay()

        self.assertTrue(TaskTransitionController(task1, {})._is_issuer())
        self.assertFalse(TaskTransitionController(task2, {})._is_issuer())
        self.assertTrue(TaskTransitionController(task3, {})._is_issuer())

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

    def test_cancelled_to_open_guards(self):
        transition = 'task-transition-cancelled-open'
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_cancelled_to_open_actions(self):
        transition = 'task-transition-cancelled-open'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def test_progress_to_resolved_guards(self):
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

    def test_progress_to_resolved_actions(self):
        transition = 'task-transition-in-progress-resolved'
        controller, controller_mock, task = self._create_task_controller()

        stc = self.stub()
        self.mock_adapter(
            stc, ISuccessorTaskController, [Interface])

        with self.mocker.order():
            # testcase 1: unival -> default form
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')

            # testcase 2: uniref -> default form
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')

            # testcase 3: not responsible -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)

            # testcase 4: no predecessor -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result(None)

            # testcase 5: no predecessor -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result('client2:213')
            self.expect(stc(task).get_predecessor().task_type).result(
                'forwarding_task_type')

            # testcase 6: -> complete task wizard
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result('client2:123')
            self.expect(stc(task).get_predecessor().task_type).result(
                'bidirectional_by_reference')

        self.replay()

        wizard_url = 'http://nohost/plone/task-1/' + \
            '@@complete_successor_task?transition=%s' % transition

        default_url = 'http://nohost/plone/task-1/addresponse?' + \
            'form.widgets.transition=%s' % transition

        # testcase 1: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 2: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 3: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 4: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 5: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 6: complete task wizard
        self.assertEqual(controller.get_transition_action(transition),
                         wizard_url)

    def test_progress_to_closed_guards(self):
        controller, controller_mock, task = self._create_task_controller()

        with self.mocker.order():
            #task1
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')

            #task2
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)

            #task3
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(
                controller_mock._is_substasks_closed()).result(False)

            #task4
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(
                controller_mock._is_substasks_closed()).result(True)
            self.expect(
                controller_mock._has_successors()).result(True)
            self.expect(controller_mock._is_remote_request()).result(False)

            #task5
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(
                controller_mock._is_substasks_closed()).result(True)
            self.expect(
                controller_mock._has_successors()).result(True)
            self.expect(controller_mock._is_remote_request()).result(True)

            #task6
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
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

    def test_progress_to_closed_actions(self):
        transition = 'task-transition-in-progress-tested-and-closed'
        controller, controller_mock, task = self._create_task_controller()

        stc = self.stub()
        self.mock_adapter(
            stc, ISuccessorTaskController, [Interface])

        with self.mocker.order():
            # testcase 1: unival -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')

            # testcase 2: uniref -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')

            # testcase 3: not responsible -> default form
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)

            # testcase 4: no predecessor -> default form
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result(None)

            # testcase 5: no predecessor -> default form
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result('client2:123')
            self.expect(stc(task).get_predecessor().task_type).result(
                'forwarding_task_type')

            # testcase 6: -> complete task wizard
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result('client2:123')
            self.expect(stc(task).get_predecessor().task_type).result(
                'unidirectional_by_reference')

        self.replay()

        wizard_url = 'http://nohost/plone/task-1/' + \
            '@@complete_successor_task?transition=%s' % transition

        default_url = 'http://nohost/plone/task-1/addresponse?' + \
            'form.widgets.transition=%s' % transition

        # testcase 1: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 2: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 3: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 4: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 5: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 6: complete task wizard
        self.assertEqual(controller.get_transition_action(transition),
                         wizard_url)

    def test_open_to_cancel_guards(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-open-cancelled'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_open_to_cancel_actions(self):
        transition = 'task-transition-open-cancelled'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def test_open_to_progress_guards(self):
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

    def test_open_to_progress_actions(self):
        transition = 'task-transition-open-in-progress'
        controller, controller_mock, task = self._create_task_controller()

        info = self.stub()
        self.mock_utility(info, IContactInformation)

        registry = self.stub()
        self.mock_utility(registry, IRegistry)
        proxy = self.stub()
        self.expect(registry.forInterface(
                IClientConfiguration)).result(proxy)
        self.expect(proxy.client_id).result('client1')

        with self.mocker.order():
            # testcase 1: single client setup
            self.expect(len(info.get_clients())).result(1)

            # testcase 2: multi client setup, same client
            self.expect(len(info.get_clients())).result(2)
            self.expect(task.responsible_client).result('client1')

            # testcase 3: multi client setup, other client
            self.expect(len(info.get_clients())).result(2)
            self.expect(task.responsible_client).result('client2')

        self.replay()

        wizard_url = 'http://nohost/plone/task-1/@@accept_choose_method'
        default_url = 'http://nohost/plone/task-1/addresponse?' + \
            'form.widgets.transition=%s' % transition

        # testcase 1: default response addform url
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 2: no need to deliver documents -> default url
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 3: document delivery wizard
        self.assertEqual(controller.get_transition_action(transition),
                         wizard_url)

    def test_open_to_reject_guards(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)

        self.replay()
        transition = 'task-transition-open-rejected'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_open_to_reject_actions(self):
        transition = 'task-transition-open-rejected'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def test_open_to_resolved_guards(self):
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

    def test_open_to_resolved_actions(self):
        transition = 'task-transition-open-resolved'
        controller, controller_mock, task = self._create_task_controller()

        successor_task_controller = self.stub()
        self.mock_adapter(
            successor_task_controller, ISuccessorTaskController, [Interface])

        with self.mocker.order():
            # testcase 1: unival -> default form
            self.expect(task.task_type_category).result(
                'unidirectional_by_value')

            # testcase 2: uniref -> default form
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')

            # testcase 3: not responsible -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                False)

            # testcase 4: no predecessor -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result(None)

            # testcase 5: no predecessor -> default form
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result('client2:123')
            self.expect(
                successor_task_controller(task).get_predecessor().task_type
                ).result('forwarding_task_type')

            # testcase 6: -> complete task wizard
            self.expect(task.task_type_category).result(
                'bidirectional_by_reference')
            self.expect(
                controller_mock._is_responsible_or_inbox_group_user()).result(
                True)
            self.expect(task.predecessor).result('client2:123')
            self.expect(
                successor_task_controller(task).get_predecessor().task_type
                ).result('bidirectional_by_reference')

        self.replay()

        wizard_url = 'http://nohost/plone/task-1/' + \
            '@@complete_successor_task?transition=%s' % transition

        default_url = 'http://nohost/plone/task-1/addresponse?' + \
            'form.widgets.transition=%s' % transition

        # testcase 1: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 2: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 3: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 4: default form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 5: predecessor is a forwarding
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 6: complete task wizard
        self.assertEqual(controller.get_transition_action(transition),
                         wizard_url)

    def test_open_to_closed_guards(self):
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

    def test_open_to_closed_actions(self):
        transition = 'task-transition-open-tested-and-closed'
        controller, controller_mock, task = self._create_task_controller()

        info = self.stub()
        self.mock_utility(info, IContactInformation)

        registry = self.stub()
        self.mock_utility(registry, IRegistry)
        proxy = self.stub()
        self.expect(registry.forInterface(
                IClientConfiguration)).result(proxy)
        self.expect(proxy.client_id).result('client1')

        catalog = self.stub()
        self.mock_tool(catalog, 'portal_catalog')
        membership = self.stub()
        self.mock_tool(membership, 'portal_membership')

        with self.mocker.order():
            # testcase 1: not uniref
            self.expect(task.task_type_category).result(
                'bidirectional_by_value')

            # testcase 2: unrief but single client setup
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(len(info.get_clients())).result(1)

            # testcase 3: unrief, multi clientbut on responsible client
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(len(info.get_clients())).result(2)
            self.expect(task.responsible_client).result('client1')

            # testcase 4: uniref, multi client, foreign client but no
            # documents to copy
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(len(info.get_clients())).result(2)
            self.expect(task.responsible_client).result('client2')
            self.expect(catalog(ANY)).result([])
            self.expect(task.relatedItems).result([])

            # testcase 5: unrief, multi client, foreign client, documents
            self.expect(task.task_type_category).result(
                'unidirectional_by_reference')
            self.expect(len(info.get_clients())).result(2)
            self.expect(task.responsible_client).result('client2')
            self.expect(catalog(ANY)).result([
                    self.create_dummy(getObject=lambda: object())])
            self.expect(task.relatedItems).result([])

        self.replay()

        wizard_url = 'http://nohost/plone/task-1/' + \
            '@@close-task-wizard_select-documents'

        default_url = 'http://nohost/plone/task-1/addresponse?' + \
            'form.widgets.transition=%s' % transition

        # testcase 1: use default response add form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 2: use default response add form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 3: use default response add form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 4: use default response add form
        self.assertEqual(controller.get_transition_action(transition),
                         default_url)

        # testcase 5: use close wizard
        self.assertEqual(controller.get_transition_action(transition),
                         wizard_url)

    def test_reassign_guards(self):
        controller, controller_mock, task = self._create_task_controller()

        self.replay()
        transition = 'task-transition-reassign'
        self.assertTrue(controller.is_transition_possible(transition))

    def test_reassign_actions(self):
        transition = 'task-transition-reassign'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/@@assign-task?' + \
                             'form.widgets.transition=%s' % transition)

    def test_rejected_to_open_guards(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-rejected-open'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_rejected_to_open_actions(self):
        transition = 'task-transition-rejected-open'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def test_resolved_to_closed_guards(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-resolved-tested-and-closed'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_resolved_to_closed_actions(self):
        transition = 'task-transition-resolved-tested-and-closed'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def test_resolved_to_progress_guards(self):
        controller, controller_mock, task = self._create_task_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_responsible_or_inbox_group_user()).result(False)

            self.expect(controller_mock._is_issuer()).result(False)
            self.expect(controller_mock._is_responsible_or_inbox_group_user()).result(True)

            self.expect(controller_mock._is_issuer()).result(True)

        self.replay()
        transition = 'task-transition-resolved-in-progress'
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))

    def test_resolved_to_progress_actions(self):
        transition = 'task-transition-resolved-in-progress'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def _create_task_controller(self):
        task1 = self.mocker.mock()
        self.expect(task1.absolute_url()).result(
            'http://nohost/plone/task-1').count(0, None)
        self.expect(task1.getPhysicalPath()).result(
            ['', 'plone', 'task-1']).count(0, None)

        controller = TaskTransitionController(task1, {})
        controller_mock = self.mocker.patch(controller)

        self.expect(controller_mock._is_administrator()).result(False).count(0, None)

        return controller, controller_mock, task1
