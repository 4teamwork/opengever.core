from DateTime import DateTime
from opengever.base.security import elevated_privileges
from opengever.task.response_syncer import BaseResponseSyncerReceiver
from opengever.task.response_syncer import BaseResponseSyncerSender
from opengever.task.response_syncer import ResponseSyncerSenderException
from plone import api
from Products.CMFCore.WorkflowCore import WorkflowException
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
            'task-transition-in-progress-tested-and-closed',
            'task-transition-resolved-in-progress',
            'task-transition-resolved-tested-and-closed',
            'task-transition-tested-and-closed-in-progress',
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

            # Because this is already teh syncing of the foreign side, we need
            # to disable syncing of the transition, otherwise it would end in
            # a snycing-loop
            try:
                wftool.doActionFor(
                    self.context, transition, disable_sync=True, transition_params=data)
            except WorkflowException:
                missmatch_fixed = self._fix_review_state_missmatch()
                if missmatch_fixed:
                    wftool.doActionFor(
                        self.context, transition,
                        disable_sync=True, transition_params=data)

        notify(ObjectModifiedEvent(self.context))

    def _fix_review_state_missmatch(self):
        """Check if there is a review_state missmatch between the predecessor
        and successor pair and fix it.

        Returns true if there was a missmatch to fix.
        """
        sql_task = self.context.get_sql_object()

        # predecessor
        if sql_task.has_remote_predecessor:
            if sql_task.predecessor.review_state != sql_task.review_state:
                self._set_review_state(sql_task.predecessor.review_state)
                return True

        if sql_task.has_remote_successor:
            # When having a remote successor there can only be one predecessor,
            # so it's safe to get the state from the first one
            if sql_task.successors[0].review_state != sql_task.review_state:
                self._set_review_state(sql_task.successors[0].review_state)
                return True

        return False

    def _set_review_state(self, review_state):
        wftool = api.portal.get_tool('portal_workflow')
        wf_id = wftool.getWorkflowsFor(self.context)[0].id
        wftool.setStatusOf(wf_id, self.context,
                           {'review_state': review_state,
                            'action': review_state,
                            'actor': 'zopemaster',
                            'time': DateTime(),
                            'comments': 'Review state missmatch synchronisation'})
        wftool.getWorkflowsFor(self.context)[0].updateRoleMappingsFor(self.context)

        self.context.sync()
        self.context.reindexObject()
