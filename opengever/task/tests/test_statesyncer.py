from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.Extensions.plugins import activate_request_layer
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import IWorkflowStateSyncer
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zExceptions import Forbidden
from zope.component import getMultiAdapter


remote_viewname = '@@sync-task-workflow-state-receive'


class TestWorkflowStateSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestWorkflowStateSyncer, self).setUp()
        activate_request_layer(self.portal.REQUEST,
                               IInternalOpengeverRequestLayer)

    def test_sync_state_change_on_successor_to_predecessor(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        successor = create(Builder('task').successor_from(predecessor))

        syncer = getMultiAdapter((successor, successor.REQUEST),
                                 IWorkflowStateSyncer)
        syncer.change_remote_tasks_workflow_state(
            'task-transition-resolved-in-progress',
            text=u'Please extend chapter 2.4')

        self.assertEquals('task-state-in-progress',
                          api.content.get_state(predecessor))

    def test_sync_state_change_on_predecessor_to_successor(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        successor = create(Builder('task')
                           .in_state('task-state-resolved')
                           .successor_from(predecessor))

        syncer = getMultiAdapter((predecessor, predecessor.REQUEST),
                                 IWorkflowStateSyncer)
        syncer.change_remote_tasks_workflow_state(
            'task-transition-resolved-in-progress',
            text=u'Please extend chapter 2.4.')

        self.assertEquals('task-state-in-progress',
                          api.content.get_state(successor))

    def test_forwarding_predecessors_are_ignored(self):
        forwarding = create(Builder('forwarding')
                            .in_state('forwarding-state-closed'))
        successor = create(Builder('task')
                           .in_state('task-state-resolved')
                           .successor_from(forwarding))

        syncer = getMultiAdapter((successor, successor.REQUEST),
                                 IWorkflowStateSyncer)
        syncer.change_remote_tasks_workflow_state(
            'task-transition-resolved-in-progress',
            text=u'Please extend chapter 2.4.')

        self.assertEquals('forwarding-state-closed',
                          api.content.get_state(forwarding))


class TestSyncerReceiveView(FunctionalTestCase):

    def setUp(self):
        super(TestSyncerReceiveView, self).setUp()
        create(Builder('ogds_user').id('hugo.boss'))

    def prepare_request(self, task, **kwargs):
        for key, value in kwargs.items():
            task.REQUEST.set(key, value)

        activate_request_layer(task.REQUEST, IInternalOpengeverRequestLayer)

    def test_receive_view_raise_forbidden_for_none_internal_requests(self):
        task = create(Builder('task'))

        with self.assertRaises(Forbidden):
            task.unrestrictedTraverse(remote_viewname)()

    def test_changes_workflow_state(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition= 'task-transition-in-progress-resolved')
        task.unrestrictedTraverse(remote_viewname)()

        self.assertEquals('task-state-resolved', api.content.get_state(task))

    def test_returns_ok_response_if_update_was_successfull(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition= 'task-transition-in-progress-resolved')
        response = task.unrestrictedTraverse(remote_viewname)()

        self.assertEquals('OK', response)

    def test_second_call_is_ignored_but_returns_ok_response(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition= 'task-transition-in-progress-resolved')
        task.unrestrictedTraverse(remote_viewname)()

        response = task.unrestrictedTraverse(remote_viewname)()
        self.assertEquals('OK', response)

    def test_does_not_reset_responsible_if_no_new_value_is_given(self):
        task = create(Builder('task')
                      .in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition= 'task-transition-in-progress-resolved')
        task.unrestrictedTraverse(remote_viewname)()

        self.assertEquals('client1', task.responsible_client)
        self.assertEquals(TEST_USER_ID, task.responsible)

    def test_updates_responsible_if_new_value_is_given(self):
        task = create(Builder('task')
                      .in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition='task-transition-reassign',
                             responsible='hugo.boss',
                             responsible_client='afi')
        task.unrestrictedTraverse(remote_viewname)()

        self.assertEquals('afi', task.responsible_client)
        self.assertEquals('hugo.boss', task.responsible)

    def test_adds_corresponding_response(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'\xe4\xe4hhh I am done!',
                             transition='task-transition-in-progress-resolved')
        task.unrestrictedTraverse(remote_viewname)()

        response = IResponseContainer(task)[-1]
        self.assertEquals('task-transition-in-progress-resolved', response.transition)
        self.assertEquals(u'\xe4\xe4hhh I am done!', response.text)
        self.assertEquals(TEST_USER_ID, response.creator)
        self.assertEquals([{'before': 'task-state-in-progress',
                            'after': 'task-state-resolved',
                            'id': 'review_state',
                            'name': u'Issue state'}], response.changes)
