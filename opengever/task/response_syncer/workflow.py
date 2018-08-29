from opengever.base.security import elevated_privileges
from opengever.task import _
from opengever.task.localroles import LocalRolesSetter
from opengever.task.response_syncer import BaseResponseSyncerReceiver
from opengever.task.response_syncer import BaseResponseSyncerSender
from opengever.task.response_syncer import ResponseSyncerSenderException
from opengever.task.task import ITask
from Products.CMFCore.utils import getToolByName
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class WorkflowResponseSyncerSender(BaseResponseSyncerSender):

    TARGET_SYNC_VIEW_NAME = '@@sync-task-workflow-response'

    def get_related_tasks_to_sync(self, transition):
        if not self._is_synced_transition(transition):
            return []

        tasks = super(WorkflowResponseSyncerSender, self).get_related_tasks_to_sync(
            transition)

        # Skip forwardings. Workflow state changes should never be
        # synced to the successor forwarding, because a forwarding predecessor
        # is allways closed and stored in the yearfolder.
        return [task for task in tasks if not task.is_forwarding]

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException(
            'Could not execute workflow transition ({}) on remote admin unit {} ({})'.format(
                transition,
                task.admin_unit_id,
                task.physical_path))

    def _is_synced_transition(self, transition):
        return transition in [
            'task-transition-in-progress-resolved',
            'task-transition-resolved-in-progress',
            'task-transition-resolved-tested-and-closed',
            'task-transition-reassign',
            ]


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

        with elevated_privileges():
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

            # Revoke local roles for current responsible
            # XXX: should be handled as a general transition-after job.
            LocalRolesSetter(self.context).revoke_roles()

            ITask(self.context).responsible_client = responsible_client
            ITask(self.context).responsible = responsible

        notify(ObjectModifiedEvent(self.context))
        response.add_change('review_state', _(u'Issue state'), before, after)
