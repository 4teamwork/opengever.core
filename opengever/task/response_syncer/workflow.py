from opengever.base.security import elevated_privileges
from opengever.task.response_syncer import BaseResponseSyncerReceiver
from opengever.task.response_syncer import BaseResponseSyncerSender
from opengever.task.response_syncer import ResponseSyncerSenderException
from plone import api
from Products.CMFPlone.utils import safe_unicode
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
        transition = self.request.get('transition')
        data = {'responsible': self.request.get('responsible'),
                'responsible_client': self.request.get('responsible_client'),
                'text': safe_unicode(text)}

        wftool = api.portal.get_tool('portal_workflow')
        with elevated_privileges():

            wftool.doActionFor(
                self.context, transition, disable_sync=True, **data)

        notify(ObjectModifiedEvent(self.context))
