from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import SimpleUser
from ftw.testing import MockTestCase
from ftw.testing.layer import ComponentRegistryLayer
from grokcore.component.testing import grok
from mocker import ANY, ARGS, KWARGS
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import IWorkflowStateSyncer
from opengever.task.statesyncer import SyncTaskWorkflowStateReceiveView
from opengever.task.task import ITask
from zExceptions import Forbidden
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


remote_viewname = '@@sync-task-workflow-state-receive'


class TestWorkflowStateSyncer(MockTestCase):

    remote_requests = []

    def setUp(self):
        super(TestWorkflowStateSyncer, self).setUp()
        grok('opengever.task.statesyncer')
        grok('opengever.task.adapters')

    def test_get_tasks_to_sync(self):
        context = self.providing_stub([ITask])
        request = self.stub()

        pred1 = self.providing_stub([ITask])
        self.expect(pred1.task_type).result(u'forwarding_task_type')
        pred2 = self.providing_stub([ITask])
        self.expect(pred2.task_type).result(u'other_task_type')
        succ1 = self.providing_stub([ITask])
        succ2 = self.providing_stub([ITask])

        stc = self.stub()
        self.mock_adapter(stc, ISuccessorTaskController, [Interface])

        self.expect(stc(context)).result(stc)
        self.expect(stc.get_successors()).result([succ1, succ2])

        with self.mocker.order():
            self.expect(stc.get_predecessor(None)).result(None)
            self.expect(stc.get_predecessor(None)).result(pred1)
            self.expect(stc.get_predecessor(None)).result(pred2)

        self.replay()

        syncer = getMultiAdapter(
            (context, request), IWorkflowStateSyncer)

        # not a transition to sync
        self.assertEquals([], syncer.get_tasks_to_sync(
            'task-transition-cancelled-open'))

        # no predecessor
        self.assertEquals([succ1, succ2], syncer.get_tasks_to_sync(
            'task-transition-resolved-in-progress'))

        # forwarding as predecessor
        self.assertEquals([succ1, succ2], syncer.get_tasks_to_sync(
            'task-transition-resolved-in-progress'))

        self.assertEquals([pred2, succ1, succ2], syncer.get_tasks_to_sync(
            'task-transition-resolved-in-progress'))

    def test_change_remote_tasks_workflow_state(self):
        context = self.providing_stub([ITask])
        request = self.stub()

        pred = self.providing_stub([ITask])
        self.expect(pred.task_type).result(u'other_task_type')
        self.expect(pred.admin_unit_id).result(u'client1')
        self.expect(pred.physical_path).result(u'path1')
        succ1 = self.providing_stub([ITask])
        self.expect(succ1.admin_unit_id).result(u'client2')
        self.expect(succ1.physical_path).result(u'path2')

        stc = self.stub()
        self.mock_adapter(stc, ISuccessorTaskController, [Interface])
        self.expect(stc(context)).result(stc)
        self.expect(stc.get_successors()).result([succ1])
        self.expect(stc.get_predecessor(None)).result(pred)
        remote_request = self.mocker.replace(
                'opengever.ogds.base.utils.remote_request')
        # from opengever.ogds.base import utils
        # utils.remote_request = lambda *a, **kw: remote_request()

        ok_response = self.stub()
        self.expect(ok_response.read().strip()).result('OK')
        self.expect(remote_request(
                u'client2',
                '@@sync-task-workflow-state-receive',
                u'path1',
                data={
                    'responsible_client': '',
                    'text': 'Simple Answer text',
                    'transition': 'task-transition-resolved-in-progress',
                    'responsible': ''})).result(ok_response).count(0, None)

        self.expect(remote_request(
                u'client2',
                '@@sync-task-workflow-state-receive',
                u'path2',
                data={
                    'responsible_client': '',
                    'text': 'Simple Answer text',
                    'transition': 'task-transition-resolved-in-progress',
                    'responsible': ''})).result(ok_response).count(0, None)

        fail_response = self.stub()
        self.expect(fail_response.read().strip()).result('Exception')

        self.expect(remote_request(
                u'client1',
                '@@sync-task-workflow-state-receive',
                u'path1',
                data={
                    'responsible_client': '',
                    'text': 'FAILING',
                    'transition': 'task-transition-resolved-tested-and-closed',
                    'responsible': ''})).result(fail_response).count(0, None)

        self.expect(remote_request(ARGS, KWARGS)).result(ok_response)

        self.replay()

        syncer = getMultiAdapter(
            (context, request), IWorkflowStateSyncer)

        self.assertEquals(
            syncer.change_remote_tasks_workflow_state(
                'task-transition-resolved-in-progress',
                u'Simple Answer text'),
            [pred, succ1])

        with self.assertRaises(Exception):
            self.assertEquals(
                syncer.change_remote_tasks_workflow_state(
                    'task-transition-resolved-tested-and-closed',
                    u'FAILING'),
                [pred, succ1]
                )


class StateSyncerZCMLLayer(ComponentRegistryLayer):

    def setUp(self):
        super(StateSyncerZCMLLayer, self).setUp()

        from zope.annotation.interfaces import IAnnotations
        from zope.annotation.attribute import AttributeAnnotations
        from zope.component import provideAdapter
        provideAdapter(AttributeAnnotations,
                       provides=IAnnotations,
                       adapts=[IAttributeAnnotatable])

        grok('opengever.task.statesyncer')
        grok('opengever.task.adapters')
        grok('opengever.task.localroles')

STATE_SYNCER_ZCML_LAYER = StateSyncerZCMLLayer()


class TestSyncTaskWorkflowStateReceiveView(MockTestCase):

    layer = STATE_SYNCER_ZCML_LAYER
    remote_requests = []

    def test_remote_view(self):
        task = self.providing_stub([ITask, IAttributeAnnotatable])
        self.expect(task.Type()).result('opengever.task.task')

        # worfklow_tool
        wft = self.stub()
        self.mock_tool(wft, 'portal_workflow')

        with self.mocker.order():
            wft.getInfoFor(task, 'review_state').result(
                'task-state-resolved')
            wft.getInfoFor(task, 'review_state').result(
                'task-state-in-progress')

        wft.doActionFor(task, u'task-transition-resolved-in-progress')
        wft.getTitleForStateOnType(
            ANY, 'opengever.task.task').result('Resolved')

        user = SimpleUser('hanspeter', '', ('manage', ), [])
        newSecurityManager(self.create_dummy(), user)

        # request
        request = self.stub_request(
            interfaces=[IInternalOpengeverRequestLayer, ],
            stub_response=False)
        getter = self.stub()
        self.expect(request.get).result(getter)
        self.expect(getter('text')).result(u'Simpletext')
        self.expect(getter('responsible')).result(None)
        self.expect(getter('responsible_client')).result(None)
        self.expect(getter('transition')).result(
            u'task-transition-resolved-in-progress')

        #response
        response = self.stub_response(request=request)
        self.expect(response.setHeader("Content-type", "text/plain"))

        self.replay()

        # NORMAL TRANSITION
        # first request
        view = SyncTaskWorkflowStateReceiveView(task, request)
        view()

        # second request should do nothing
        view = SyncTaskWorkflowStateReceiveView(task, request)
        view()

        self.assertEquals(len(IResponseContainer(task)), 1)
        self.assertEquals(IResponseContainer(task)[0].text, u'Simpletext')
        self.assertEquals(len(IResponseContainer(task)[0].changes), 1)
        self.assertEquals(IResponseContainer(task)[0].creator, 'hanspeter')

    def test_reassign_remote_view(self):

        task = self.providing_stub([ITask, IAttributeAnnotatable])
        self.expect(task.Type()).result('opengever.task.task')
        self.expect(task.responsible).result('old_responsible')
        task.responsible = 'hugo.boss'

        # worfklow_tool
        wft = self.stub()
        self.mock_tool(wft, 'portal_workflow')

        with self.mocker.order():
            wft.getInfoFor(task, 'review_state').result(
                'task-state-resolved')
            wft.getInfoFor(task, 'review_state').result(
                'task-state-in-progress')

        wft.doActionFor(task, u'task-transition-reassign')
        wft.getTitleForStateOnType(
            ANY, 'opengever.task.task').result('Resolved')

        user = SimpleUser('hanspeter', '', ('manage', ), [])
        newSecurityManager(self.create_dummy(), user)

        # reassign request
        reassign_request = self.stub_request(
            interfaces=[IInternalOpengeverRequestLayer, ],
            stub_response=False)
        getter = self.stub()
        self.expect(reassign_request.get).result(getter)
        self.expect(getter('text')).result(u'Simpletext')
        self.expect(getter('responsible')).result('hugo.boss')
        self.expect(getter('responsible_client')).result('client1')
        self.expect(getter('transition')).result(
            u'task-transition-reassign')

        # reassign respone
        response = self.stub_response(request=reassign_request)
        self.expect(response.setHeader("Content-type", "text/plain"))

        # an ObjectModifiedEvent should be notified to update the local roles
        handler = self.stub()
        self.mock_handler(handler, [IObjectModifiedEvent])
        self.expect(handler(ANY)).result(True)

        self.replay()

        # REASSIGN TRANSITION
        # first request
        view = SyncTaskWorkflowStateReceiveView(task, reassign_request)
        view()

        self.assertEquals(IResponseContainer(task)[0].text, u'Simpletext')
        self.assertEquals(len(IResponseContainer(task)), 1)

    def test_forbidden(self):
        task = self.providing_stub([ITask, IAttributeAnnotatable])
        request = self.stub_request()
        getter = self.stub()
        self.expect(request.get).result(getter)

        self.replay()

        with self.assertRaises(Forbidden):
            SyncTaskWorkflowStateReceiveView(task, request)()

    def test_test_and_closed_sync(self):
        """The responsible value None is given in string (remote_request)
        the responsible should not be set."""

        task = self.providing_stub([ITask, IAttributeAnnotatable])
        self.expect(task.Type()).result('opengever.task.task')

        # request
        request = self.stub_request(
            interfaces=[IInternalOpengeverRequestLayer, ],
            stub_response=False)
        getter = self.stub()
        self.expect(request.get).result(getter)
        self.expect(getter('text')).result(u'Closing text')
        self.expect(getter('responsible')).result('None')
        self.expect(getter('responsible_client')).result('None')
        self.expect(getter('transition')).result(
            u'task-transition-tested-and-closed')

        #response
        response = self.stub_response(request=request)
        self.expect(response.setHeader("Content-type", "text/plain"))

        # worfklow_tool
        wft = self.stub()
        self.mock_tool(wft, 'portal_workflow')

        with self.mocker.order():
            wft.getInfoFor(task, 'review_state').result(
                'task-state-in-progress')
            wft.getInfoFor(task, 'review_state').result(
                'task-state-tested-and-closed')

        wft.doActionFor(task, u'task-transition-tested-and-closed')
        wft.getTitleForStateOnType(
            ANY, 'opengever.task.task').result('Closed')

        self.replay()

        view = SyncTaskWorkflowStateReceiveView(task, request)
        view()

        self.assertEquals(IResponseContainer(task)[0].text, u'Closing text')
        self.assertEquals(len(IResponseContainer(task)), 1)
