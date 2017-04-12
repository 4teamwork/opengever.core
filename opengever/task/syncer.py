from datetime import date
from opengever.base.request import dispatch_request
from opengever.base.utils import ok_response
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.task import _
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import ICommentResponseSyncerSender
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.interfaces import IModifyDeadlineResponseSyncerSender
from opengever.task.interfaces import IResponseSyncerSender
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import IWorkflowResponseSyncerSender
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from Products.CMFCore.utils import getToolByName
from Products.CMFDiffTool.utils import safe_utf8
from Products.Five import BrowserView
from zExceptions import Forbidden
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
import AccessControl


class ResponseSyncerSenderException(Exception):
    """An exception raised if something went wrong while syncing
    the response-object.
    """


class BaseResponseSyncerSender(object):
    """Abstract ResponseSyncerSender base class for performing a task sync between
    admin-units. This class is responsible for sending the data to other admin-units
    """
    implements(IResponseSyncerSender)

    TARGET_SYNC_VIEW_NAME = None  # Nedds to be defined in a subclass

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sync_related_tasks(self, transition, text, **kwargs):
        tasks = self.get_related_tasks_to_sync(transition)
        for task in tasks:
            self.sync_related_task(task, transition, text, **kwargs)

        return tasks

    def get_related_tasks_to_sync(self, transition=''):
        tasks = []
        stc = ISuccessorTaskController(self.context)
        predecessor = stc.get_predecessor(None)
        if predecessor:
            tasks.append(predecessor)

        tasks.extend(stc.get_successors())

        return tasks

    def sync_related_task(self, task, transition, text, **kwargs):
        payload = {'transition': transition,
                   'text': safe_utf8(text)}
        self.extend_payload(payload, task, **kwargs)

        response = self._dispatch_request(
            task.admin_unit_id,
            self.TARGET_SYNC_VIEW_NAME,
            task.physical_path,
            data=payload)

        response_data = response.read().strip()
        if response_data != 'OK':
            self.raise_sync_exception(task, transition, text, **kwargs)

    def extend_payload(self, payload, task, **kwargs):
        payload.update(kwargs)

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException()

    def _dispatch_request(self, target_admin_unit_id, viewname, path, data):
        return dispatch_request(target_admin_unit_id, viewname, path, data)


class CommentResponseSyncerSender(BaseResponseSyncerSender):
    implements(ICommentResponseSyncerSender)

    TARGET_SYNC_VIEW_NAME = '@@sync-task-comment-response'

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException(
            'Could not add comment on task on remote admin unit {} ({})'.format(
                task.admin_unit_id,
                task.physical_path))


class WorkflowResponseSyncerSender(BaseResponseSyncerSender):
    implements(IWorkflowResponseSyncerSender)

    TARGET_SYNC_VIEW_NAME = '@@sync-task-workflow-response'

    def get_related_tasks_to_sync(self, transition):
        if not self._is_synced_transition(transition):
            return []
        return super(WorkflowResponseSyncerSender, self).get_related_tasks_to_sync(transition)

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException(
            'Could not change workflow on remote admin unit {} ({})'.format(
                task.admin_unit_id,
                task.physical_path))

    def _is_synced_transition(self, transition):
        return transition in [
            'task-transition-resolved-in-progress',
            'task-transition-resolved-tested-and-closed',
            'task-transition-reassign',
            ]


class ModifyDeadlineResponseSyncerSender(BaseResponseSyncerSender):
    implements(IModifyDeadlineResponseSyncerSender)

    TARGET_SYNC_VIEW_NAME = '@@sync-task-modify-deadline-response'

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException(
            'Updating deadline on remote client {}. failed ({})'.format(
                task.admin_unit_id,
                task.physical_path))

    def extend_payload(self, payload, task, **kwargs):
        kwargs['new_deadline'] = kwargs['new_deadline'].toordinal()
        super(ModifyDeadlineResponseSyncerSender, self).extend_payload(payload, task, **kwargs)


class BaseResponseSyncerReceiver(BrowserView):
    """Abstract ResponseSyncerReceiver view for receiving requests from a
    ResponseSyncerSender and updates the current task with the received data

    The view returns "OK" if everything went fine.
    The view will raise a Forbidden-Exception if the user is not allowed to use
    this view.
    """

    def __call__(self):
        self._check_internal_request()

        transition = self.request.get('transition')
        text = self.request.get('text')

        if self._is_already_done(transition, text):
            return ok_response(self.request)

        self._update(transition, text)
        return ok_response(self.request)

    def _update(self, transition, text):
        """Updates the current task with the received data
        """
        return add_simple_response(self.context, transition=transition, text=text)

    def _check_internal_request(self):
        # WARNING: The security is done here by using the request layer
        # IInternalOpengeverRequestLayer provided by the ogds PAS plugin.
        # The view has to be public, since the user may not have any
        # permission on this context.
        if not IInternalOpengeverRequestLayer.providedBy(self.request):
            raise Forbidden()

    def _is_already_done(self, transition, text):
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


class CommentResponseSyncerReceiver(BaseResponseSyncerReceiver):
    """This view receives a sync-task-comment-response request from another
    client after new comments have been added to a successor or predecessor.
    """


class WorkflowResponseSyncerReceiver(BaseResponseSyncerReceiver):
    """This view receives a sync-task-workflow-state request from another
    client after a successor or predecessor has changed the workflow state.
    """

    def _update(self, transition, text):
        response = super(WorkflowResponseSyncerReceiver, self)._update(transition, text)

        transition = self.request.get('transition')
        responsible = self.request.get('responsible')
        responsible_client = self.request.get('responsible_client')

        wftool = getToolByName(self.context, 'portal_workflow')

        # change workflow state
        before = wftool.getInfoFor(self.context, 'review_state')
        before = wftool.getTitleForStateOnType(before, self.context.Type())

        wftool.doActionFor(self.context, transition)

        after = wftool.getInfoFor(self.context, 'review_state')
        after = wftool.getTitleForStateOnType(after, self.context.Type())

        if responsible and responsible is not 'None':
            # special handling for reassign
            response.add_change(
                'responsible',
                _(u"label_responsible", default=u"Responsible"),
                ITask(self.context).responsible,
                responsible)

            ITask(self.context).responsible_client = responsible_client
            ITask(self.context).responsible = responsible

            notify(ObjectModifiedEvent(self.context))

        response.add_change('review_state', _(u'Issue state'),
                            before, after)


class ModifyDeadlineResponseSyncerReceiver(BaseResponseSyncerReceiver):
    """This view receives a sync-task-modify-deadline-response request from another
    client after a successor or predecessor has changed the deadline.
    """

    def _update(self, transition, text):
        new_deadline = self.request.get('new_deadline', None)
        new_deadline = date.fromordinal(int(new_deadline))
        text = self.request.get('text', u'')
        transition = self.request.get('transition')

        IDeadlineModifier(self.context).update_deadline(
            new_deadline, text, transition)
