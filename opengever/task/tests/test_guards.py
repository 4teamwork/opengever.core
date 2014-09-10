from ftw.testing import MockTestCase
from opengever.task.browser.transitioncontroller import ITaskTransitionController
from opengever.task.browser.transitioncontroller import TaskTransitionController
from opengever.task.interfaces import ISuccessorTaskController
from Products.CMFPlone.interfaces import IPloneSiteRoot
from xml.dom.minidom import parse
from zope.app.component.hooks import setSite
from zope.component import getSiteManager
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface.verify import verifyClass
import os.path


class TestTaskTransitionController(MockTestCase):

    def setUp(self):
        super(TestTaskTransitionController, self).setUp()
        # we need to have a site root for making the cachecky work.
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
            self.expect(mock.has_role('Administrator')).result(0)
            self.expect(mock.has_role('Manager')).result(0)

            self.expect(mock.has_role('Administrator')).result(0)
            self.expect(mock.has_role('Manager')).result(1)

            self.expect(mock.has_role('Administrator')).result(1)

        self.replay()

        self.assertFalse(
            TaskTransitionController(task1, {})._is_administrator())
        self.assertTrue(
            TaskTransitionController(task1, {})._is_administrator())
        self.assertTrue(
            TaskTransitionController(task1, {})._is_administrator())

    def test_cancelled_to_open_actions(self):
        transition = 'task-transition-cancelled-open'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

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

    def test_open_to_cancel_actions(self):
        transition = 'task-transition-open-cancelled'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def test_open_to_reject_actions(self):
        transition = 'task-transition-open-rejected'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

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



    def test_reassign_actions(self):
        transition = 'task-transition-reassign'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/@@assign-task?' + \
                             'form.widgets.transition=%s' % transition)

    def test_rejected_to_open_actions(self):
        transition = 'task-transition-rejected-open'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

    def test_resolved_to_closed_actions(self):
        transition = 'task-transition-resolved-tested-and-closed'
        controller, controller_mock, task = self._create_task_controller()

        self.replay()

        self.assertEqual(controller.get_transition_action(transition),
                         'http://nohost/plone/task-1/addresponse?' + \
                             'form.widgets.transition=%s' % transition)

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
