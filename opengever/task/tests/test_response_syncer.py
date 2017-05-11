from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.Extensions.plugins import activate_request_layer
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import IResponseSyncerSender
from opengever.task.response_syncer import BaseResponseSyncerReceiver
from opengever.task.response_syncer import BaseResponseSyncerSender
from opengever.task.response_syncer import ResponseSyncerSenderException
from opengever.task.response_syncer.comment import CommentResponseSyncerSender
from opengever.task.response_syncer.deadline import ModifyDeadlineResponseSyncerSender
from opengever.task.response_syncer.workflow import WorkflowResponseSyncerSender
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
import datetime


class MockDispatchRequest(object):

    def __init__(self, response):
        self.requests = []
        self.response = response

    def __call__(self, target_admin_unit_id, viewname, path, data):
        self.requests.append({
            'target_admin_unit_id': target_admin_unit_id,
            'viewname': viewname,
            'path': path,
            'data': data,
        })

        return self

    def read(self):
        return self.response


class TestBaseResponseSyncerSender(FunctionalTestCase):

    def _mock_dispatch_request(self, sender, response):
        mock = MockDispatchRequest(response=response)
        sender._dispatch_request = mock
        return mock

    def test_verify_interfaces(self):
        verifyClass(IResponseSyncerSender, BaseResponseSyncerSender)

    def test_sync_related_tasks_raises_an_exception_if_syncing_failed(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        create(Builder('task').successor_from(predecessor))

        sender = BaseResponseSyncerSender(predecessor, self.request)
        sender.TARGET_SYNC_VIEW_NAME = "NOT_EXISTING_VIEW"

        self._mock_dispatch_request(sender, 'NOT_FOUND')

        with self.assertRaises(ResponseSyncerSenderException):
            sender.sync_related_tasks('', '')

    def test_sync_related_tasks_performs_a_request_for_each_successor(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        create(Builder('task').successor_from(predecessor))
        create(Builder('task').successor_from(predecessor))

        sender = BaseResponseSyncerSender(predecessor, self.request)
        sender.TARGET_SYNC_VIEW_NAME = "SYNC_TASK"
        mock_request = self._mock_dispatch_request(sender, 'OK')

        sender.sync_related_tasks('test-transition', u't\xe4st')

        self.assertEqual(
            2, len(mock_request.requests),
            "The syncer should have made two requests. One for each successor")

        self.assertItemsEqual(
            [
                {'data': {'text': 't\xc3\xa4st', 'transition': 'test-transition'},
                 'path': u'task-2',
                 'target_admin_unit_id': u'client1',
                 'viewname': 'SYNC_TASK'},
                {'data': {'text': 't\xc3\xa4st', 'transition': 'test-transition'},
                 'path': u'task-3',
                 'target_admin_unit_id': u'client1',
                 'viewname': 'SYNC_TASK'}
            ],
            mock_request.requests
        )

    def test_sync_related_task_raises_an_exception_if_syncing_failed(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        create(Builder('task').successor_from(predecessor))

        sender = BaseResponseSyncerSender(predecessor, self.request)
        sender.TARGET_SYNC_VIEW_NAME = "NOT_EXISTING_VIEW"

        self._mock_dispatch_request(sender, 'NOT_FOUND')

        task = sender.get_related_tasks_to_sync()[0]
        with self.assertRaises(ResponseSyncerSenderException):
            sender.sync_related_task(task, '', '')

    def test_sync_related_task_performs_a_request_to_the_target_sync_view_name(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        create(Builder('task').successor_from(predecessor))

        sender = BaseResponseSyncerSender(predecessor, self.request)
        sender.TARGET_SYNC_VIEW_NAME = "SYNC_TASK"
        mock_request = self._mock_dispatch_request(sender, 'OK')

        task = sender.get_related_tasks_to_sync()[0]
        sender.sync_related_task(task, 'test-transition', u't\xe4st', firstname='james')

        self.assertItemsEqual(
            [
                {'data': {'text': 't\xc3\xa4st',
                          'transition': 'test-transition',
                          'firstname': 'james'},
                 'path': u'task-2',
                 'target_admin_unit_id': u'client1',
                 'viewname': 'SYNC_TASK'},
            ],
            mock_request.requests
        )

    def test_get_related_tasks_to_sync_returns_empty_list_if_there_are_no_successors_or_predecessors(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))

        sender = BaseResponseSyncerSender(predecessor, self.request)

        self.assertEqual([], sender.get_related_tasks_to_sync())

    def test_get_related_tasks_to_sync_returns_all_successors_in_a_list(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        successor_1 = create(Builder('task').successor_from(predecessor))
        successor_2 = create(Builder('task').successor_from(predecessor))

        sender = BaseResponseSyncerSender(predecessor, self.request)

        tasks = sender.get_related_tasks_to_sync()

        self.assertItemsEqual([
            successor_1.get_sql_object(), successor_2.get_sql_object()],
            tasks)

    def test_get_related_tasks_to_sync_returns_predecessor_in_a_list(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        successor_1 = create(Builder('task').successor_from(predecessor))

        sender = BaseResponseSyncerSender(successor_1, self.request)

        tasks = sender.get_related_tasks_to_sync()

        self.assertEqual([predecessor.get_sql_object()], tasks)

    def test_extend_payload_updates_payload_with_kwargs(self):
        sender = BaseResponseSyncerSender(object(), self.request)

        payload = {'text': 'My text'}
        sender.extend_payload(payload, object(), firstname="james", lastname="bond")

        self.assertEqual({
            'text': 'My text',
            'firstname': 'james',
            'lastname': 'bond'},
            payload)

    def test_raise_sync_exception_raises_an_exception(self):
        sender = BaseResponseSyncerSender(object(), self.request)

        with self.assertRaises(ResponseSyncerSenderException):
            sender.raise_sync_exception(object(), '', '')


class TestCommentResponseSyncerSender(FunctionalTestCase):

    def test_verify_interfaces(self):
        verifyClass(IResponseSyncerSender, CommentResponseSyncerSender)

    def test_raises_sync_exception_raises_comment_specific_exception_message(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))

        sender = CommentResponseSyncerSender(object(), self.request)

        with self.assertRaises(ResponseSyncerSenderException) as exception:
            sender.raise_sync_exception(
                predecessor.get_sql_object(),
                'comment-transition', 'some text')

        self.assertEqual(
            'Could not add comment on task on remote admin unit client1 (task-1)',
            str(exception.exception))


class TestWorkflowResponseSyncerSender(FunctionalTestCase):

    def test_verify_interfaces(self):
        verifyClass(IResponseSyncerSender, WorkflowResponseSyncerSender)

    def test_raises_sync_exception_raises_workflow_specific_exception_message(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))

        sender = WorkflowResponseSyncerSender(object(), self.request)

        with self.assertRaises(ResponseSyncerSenderException) as exception:
            sender.raise_sync_exception(
                predecessor.get_sql_object(),
                'publish', 'some text')

        self.assertEqual(
            'Could not execute workflow transition (publish) on remote admin unit client1 (task-1)',
            str(exception.exception))

    def test_forwarding_predecessors_are_ignored(self):
        forwarding = create(Builder('forwarding')
                            .in_state('forwarding-state-closed'))
        successor = create(Builder('task')
                           .in_state('task-state-in-progress')
                           .successor_from(forwarding))

        sender = WorkflowResponseSyncerSender(successor, self.request)
        self.assertEqual(
            [], sender.get_related_tasks_to_sync(transition='task-transition-reassign'))

    def test_task_predecessors_are_synced(self):
        task = create(Builder('task')
                            .in_state('task-state-in-progress'))
        successor = create(Builder('task')
                           .in_state('task-state-in-progress')
                           .successor_from(task))

        sender = WorkflowResponseSyncerSender(successor, self.request)
        self.assertEqual(
            [task.get_sql_object()],
            sender.get_related_tasks_to_sync(transition='task-transition-reassign'))


class TestModifyDeadlineResponseSyncerSender(FunctionalTestCase):

    def test_verify_interfaces(self):
        verifyClass(IResponseSyncerSender, ModifyDeadlineResponseSyncerSender)

    def test_raises_sync_exception_raises_modify_deadline_specific_exception_message(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))

        sender = ModifyDeadlineResponseSyncerSender(object(), self.request)

        with self.assertRaises(ResponseSyncerSenderException) as exception:
            sender.raise_sync_exception(
                predecessor.get_sql_object(),
                'modify-deadline-transition', 'some text')

        self.assertEqual(
            'Updating deadline on remote client client1. failed (task-1)',
            str(exception.exception))

    def test_extend_payload_safes_the_deadline_ordinal_number(self):
        sender = ModifyDeadlineResponseSyncerSender(object(), self.request)

        new_deadline = datetime.date(2013, 1, 1)

        payload = {}
        sender.extend_payload(payload, object(), new_deadline=new_deadline)

        self.assertEqual({'new_deadline': new_deadline.toordinal()}, payload)


class TestBaseResponseSyncerReceiver(FunctionalTestCase):

    def prepare_request(self, task, **kwargs):
        for key, value in kwargs.items():
            task.REQUEST.set(key, value)

        activate_request_layer(task.REQUEST, IInternalOpengeverRequestLayer)

    def test_receive_view_raise_forbidden_for_none_internal_requests(self):
        task = create(Builder('task'))

        with self.assertRaises(Forbidden):
            BaseResponseSyncerReceiver(task, self.request)()

    def test_adds_a_response_to_the_given_context(self):
        task = create(Builder('task'))

        self.prepare_request(task, text=u'Response text',
                             transition='base-response')

        BaseResponseSyncerReceiver(task, self.request)()

        response_container = IResponseContainer(task)
        self.assertEqual(1, len(response_container))

        response = response_container[0]

        self.assertEqual('Response text', response.text)
        self.assertEqual('base-response', response.transition)

    def test_do_not_add_the_same_response_twice_but_return_ok_anyway(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'Response text!',
                             transition='base-response')

        receiver = BaseResponseSyncerReceiver(task, self.request)

        self.assertEquals('OK', receiver())
        self.assertEquals('OK', receiver())

        response_container = IResponseContainer(task)
        self.assertEqual(
            1, len(response_container),
            "Should not add the same response twice")


class TestWorkflowSyncerReceiver(FunctionalTestCase):

    RECEIVER_VIEW_NAME = '@@sync-task-workflow-response'

    def prepare_request(self, task, **kwargs):
        for key, value in kwargs.items():
            task.REQUEST.set(key, value)

        activate_request_layer(task.REQUEST, IInternalOpengeverRequestLayer)

    def test_changes_workflow_state(self):
        task = create(Builder('task').in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition= 'task-transition-in-progress-resolved')

        task.unrestrictedTraverse(self.RECEIVER_VIEW_NAME)()

        self.assertEquals('task-state-resolved', api.content.get_state(task))

    def test_does_not_reset_responsible_if_no_new_value_is_given(self):
        task = create(Builder('task')
                      .in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition= 'task-transition-in-progress-resolved')
        task.unrestrictedTraverse(self.RECEIVER_VIEW_NAME)()

        self.assertEquals('client1', task.responsible_client)
        self.assertEquals(TEST_USER_ID, task.responsible)

    def test_updates_responsible_if_new_value_is_given(self):
        create(Builder('ogds_user').id('hugo.boss'))
        task = create(Builder('task')
                      .in_state('task-state-in-progress'))

        self.prepare_request(task, text=u'I am done!',
                             transition='task-transition-reassign',
                             responsible='hugo.boss',
                             responsible_client='afi')
        task.unrestrictedTraverse(self.RECEIVER_VIEW_NAME)()

        self.assertEquals('afi', task.responsible_client)
        self.assertEquals('hugo.boss', task.responsible)


class TestModifyDeadlineSyncerReceiver(FunctionalTestCase):

    RECEIVER_VIEW_NAME = '@@sync-task-modify-deadline-response'

    def prepare_request(self, task, **kwargs):
        for key, value in kwargs.items():
            task.REQUEST.set(key, value)

        activate_request_layer(task.REQUEST, IInternalOpengeverRequestLayer)

    def test_changes_task_deadline(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1)))

        self.prepare_request(task, text=u'I am done!',
                             transition='task-transition-modify-deadline',
                             new_deadline=datetime.date(2013, 10, 1).toordinal())

        task.unrestrictedTraverse(self.RECEIVER_VIEW_NAME)()

        self.assertEquals(task.deadline, datetime.date(2013, 10, 1))

    def test_according_response_is_added_when_modify_deadline(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1)))

        self.prepare_request(task, text=u'Lorem Ipsum',
                             transition='task-transition-modify-deadline',
                             new_deadline=datetime.date(2013, 10, 1).toordinal())

        task.unrestrictedTraverse(self.RECEIVER_VIEW_NAME)()

        container = IResponseContainer(task)
        response = container[-1]

        self.assertEquals('Lorem Ipsum', response.text)
        self.assertEquals(TEST_USER_ID, response.creator)
        self.assertEquals(
            [{'after': datetime.date(2013, 10, 1),
              'id': 'deadline',
              'name': u'label_deadline',
              'before': datetime.date(2013, 1, 1)}],
            response.changes)


class TestCommentSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestCommentSyncer, self).setUp()
        activate_request_layer(self.portal.REQUEST,
                               IInternalOpengeverRequestLayer)

    def test_sync_comment_on_successor_to_predecessor(self):
        predecessor = create(Builder('task'))
        successor = create(Builder('task').successor_from(predecessor))

        sender = getMultiAdapter((successor, successor.REQUEST),
                                 IResponseSyncerSender, name='comment')

        sender.sync_related_tasks('task-commented', text=u'We need more stuff!')

        response_container = IResponseContainer(predecessor)
        self.assertEqual(1, len(response_container))

        response = response_container[0]

        self.assertEqual('We need more stuff!', response.text)
        self.assertEqual('task-commented', response.transition)

    def test_sync_comment_on_predecessor_to_successor(self):
        predecessor = create(Builder('task'))
        successor = create(Builder('task')
                           .successor_from(predecessor))

        sender = getMultiAdapter((predecessor, predecessor.REQUEST),
                                 IResponseSyncerSender, name='comment')

        sender.sync_related_tasks('task-commented', text=u'We need more stuff!')

        response_container = IResponseContainer(successor)
        self.assertEqual(1, len(response_container))

        response = response_container[0]

        self.assertEqual('We need more stuff!', response.text)
        self.assertEqual('task-commented', response.transition)


class TestWorkflowSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestWorkflowSyncer, self).setUp()
        activate_request_layer(self.portal.REQUEST,
                               IInternalOpengeverRequestLayer)

    def test_sync_state_change_on_successor_to_predecessor(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        successor = create(Builder('task').successor_from(predecessor))

        sender = WorkflowResponseSyncerSender(successor, self.request)

        sender.sync_related_tasks(
            'task-transition-resolved-in-progress',
            text=u'Please extend chapter 2.4')

        self.assertEquals('task-state-in-progress',
                          api.content.get_state(predecessor))

    def test_sync_state_change_on_predecessor_to_successor(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        successor = create(Builder('task')
                           .in_state('task-state-resolved')
                           .successor_from(predecessor))

        sender = WorkflowResponseSyncerSender(predecessor, self.request)

        sender.sync_related_tasks(
            'task-transition-resolved-in-progress',
            text=u'Please extend chapter 2.4.')

        self.assertEquals('task-state-in-progress',
                          api.content.get_state(successor))

    def test_adds_corresponding_response(self):
        predecessor = create(Builder('task'))
        successor = create(Builder('task')
                           .successor_from(predecessor)
                           .in_state('task-state-in-progress'))

        sender = WorkflowResponseSyncerSender(predecessor, self.request)

        sender.sync_related_tasks(
            'task-transition-in-progress-resolved',
            text=u'\xe4\xe4hhh I am done!')

        response = IResponseContainer(successor)[-1]
        self.assertEquals('task-transition-in-progress-resolved', response.transition)
        self.assertEquals('\xc3\xa4\xc3\xa4hhh I am done!', response.text)
        self.assertEquals(TEST_USER_ID, response.creator)
        self.assertEquals([{'before': 'task-state-in-progress',
                            'after': 'task-state-resolved',
                            'id': 'review_state',
                            'name': u'Issue state'}], response.changes)


class TestModifyDeadlineSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestModifyDeadlineSyncer, self).setUp()
        activate_request_layer(self.portal.REQUEST,
                               IInternalOpengeverRequestLayer)

    def test_sync_deadline_modification_on_successor_to_predecessor(self):
        predecessor = create(Builder('task').having(deadline=datetime.date(2013, 1, 1)))
        successor = create(Builder('task').successor_from(predecessor))

        sender = ModifyDeadlineResponseSyncerSender(successor, self.request)
        sender.sync_related_tasks(
            'task-transition-modify-deadline',
            text=u'New deadline',
            new_deadline=datetime.date(2013, 10, 1))

        self.assertEquals(predecessor.deadline, datetime.date(2013, 10, 1))

    def test_sync_deadline_modification_on_predecessor_to_successor(self):
        predecessor = create(Builder('task').in_state('task-state-resolved'))
        successor = create(Builder('task')
                           .having(deadline=datetime.date(2013, 1, 1))
                           .successor_from(predecessor))

        sender = ModifyDeadlineResponseSyncerSender(predecessor, self.request)
        sender.sync_related_tasks(
            'task-transition-modify-deadline',
            text=u'New deadline',
            new_deadline=datetime.date(2013, 10, 1))

        self.assertEquals(successor.deadline, datetime.date(2013, 10, 1))
