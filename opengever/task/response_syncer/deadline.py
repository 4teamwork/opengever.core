from datetime import date
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.response_syncer import BaseResponseSyncerReceiver
from opengever.task.response_syncer import BaseResponseSyncerSender
from opengever.task.response_syncer import ResponseSyncerSenderException


class ModifyDeadlineResponseSyncerSender(BaseResponseSyncerSender):

    TARGET_SYNC_VIEW_NAME = '@@sync-task-modify-deadline-response'

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException(
            'Updating deadline on remote client {}. failed ({})'.format(
                task.admin_unit_id,
                task.physical_path))

    def extend_payload(self, payload, task, **kwargs):
        kwargs['new_deadline'] = kwargs['new_deadline'].toordinal()
        super(ModifyDeadlineResponseSyncerSender, self).extend_payload(payload, task, **kwargs)

    def get_related_tasks_to_sync(self, transition=''):
        """Skip forwarding predecessors. Forwarding predecessors are already
        closed and stored in the yearfolder, and should not be changed.
        """

        tasks = super(ModifyDeadlineResponseSyncerSender, self).get_related_tasks_to_sync(
            transition=transition)
        return [task for task in tasks if not task.is_forwarding]


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

    def _is_already_done(self, transition, text):
        """_is_already_done from the BaseResponseSyncerReceiver only checks
        that text, creator and transition match, but in the case of a deadline
        modification, the same user can very well modify the deadline with the
        same comment twice in a row. We therefore also check whether the current
        deadline also matches the new_deadline being set. This should be enough
        as the UI does not allow changing the deadline to the same date.
        """
        already_done = super(ModifyDeadlineResponseSyncerReceiver, self)._is_already_done(transition, text)
        if not already_done:
            return False
        new_deadline = self.request.get('new_deadline', None)
        new_deadline = date.fromordinal(int(new_deadline))
        return self.context.deadline == new_deadline
