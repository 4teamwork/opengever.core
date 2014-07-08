"""The state syncer syncs workflow states of related tasks (successors and
predecessors).
"""
from five import grok
from opengever.base.utils import ok_response
from opengever.ogds.base import utils
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.task import _
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import IWorkflowStateSyncer
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from Products.CMFCore.utils import getToolByName
from zExceptions import Forbidden
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent
import AccessControl


class WorkflowStateSyncer(grok.MultiAdapter):
    grok.adapts(ITask, Interface)
    grok.provides(IWorkflowStateSyncer)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_tasks_to_sync(self, transition):
        if not self._is_synced_transition(transition):
            return []

        tasks = []
        stc = ISuccessorTaskController(self.context)

        predecessor = stc.get_predecessor(None)

        #Fowarding predecessors should not be synced.
        if (predecessor is not None and
            predecessor.task_type != u'forwarding_task_type'):
            tasks.append(predecessor)

        tasks.extend(stc.get_successors())

        return tasks

    def change_remote_tasks_workflow_state(
        self, transition, text, responsible='', responsible_client=''):

        tasks = self.get_tasks_to_sync(transition)
        if not tasks:
            return False

        for task in tasks:

            response = utils.remote_request(
                task.admin_unit_id,
                '@@sync-task-workflow-state-receive',
                task.physical_path,
                data={'transition': transition,
                      'text': text and text.encode('utf-8') or '',
                      'responsible': responsible,
                      'responsible_client': responsible_client})

            response_data = response.read().strip()
            if response_data != 'OK':
                raise Exception(
                    'Could not change task on remote client %s (%s)' % (
                        task.client_id,
                        task.physical_path))

        return tasks

    def _is_synced_transition(self, transition):
        return transition in [
            'task-transition-resolved-in-progress',
            'task-transition-resolved-tested-and-closed',
            'task-transition-reassign',
            ]


class SyncTaskWorkflowStateReceiveView(grok.View):
    """This view receives a sync-task-workflow-state request from another
    client after a related task has changed the workflow state.

    The view returns "OK" if all went fine.
    """

    grok.context(ITask)
    grok.name('sync-task-workflow-state-receive')

    # WARNING: The security is done here by using the request layer
    # IInternalOpengeverRequestLayer provided by the ogds PAS plugin.
    # The view has to be public, since the user may not have any
    # permission on this context.
    # grok.layer(IInternalOpengeverRequestLayer)
    # grok.require('zope2.Public')

    def render(self):

        if not IInternalOpengeverRequestLayer.providedBy(self.request):
            raise Forbidden()

        transition = self.request.get('transition')
        text = self.request.get('text')
        responsible = self.request.get('responsible')
        responsible_client = self.request.get('responsible_client')

        if self.is_already_done(transition, text):
            return ok_response(self.request)

        wftool = getToolByName(self.context, 'portal_workflow')

        # change workflow state
        before = wftool.getInfoFor(self.context, 'review_state')
        before = wftool.getTitleForStateOnType(before, self.context.Type())

        wftool.doActionFor(self.context, transition)

        after = wftool.getInfoFor(self.context, 'review_state')
        after = wftool.getTitleForStateOnType(after, self.context.Type())

        # create response
        response = add_simple_response(
            self.context,
            transition=transition,
            text=text)

        if responsible and responsible is not 'None':
            # special handling for reassign
            response.add_change(
                'reponsible',
                _(u"label_responsible", default=u"Responsible"),
                ITask(self.context).responsible,
                responsible)

            ITask(self.context).responsible_client = responsible_client
            ITask(self.context).responsible = responsible

            notify(ObjectModifiedEvent(self.context))

        response.add_change('review_state', _(u'Issue state'),
                            before, after)

        return ok_response(self.request)

    def is_already_done(self, transition, text):
        """This method returns `True` if this exact request was already
        executed.
        This is the case when the sender client has a conflict error when
        committing and the sender-request needs to be re-done. In this case
        this view is called another time but the changes were already made
        and committed - so we need to return "OK" and do nothing.
        """

        response_container = IResponseContainer(self.context)
        if len(response_container) == 0:
            return False

        last_response = response_container[-1]
        current_user = AccessControl.getSecurityManager().getUser()

        if last_response.transition == transition and \
                last_response.creator == current_user.getId() and \
                last_response.text == text:
            return True

        else:
            return False
