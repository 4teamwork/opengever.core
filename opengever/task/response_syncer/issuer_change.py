from opengever.base.utils import ok_response
from opengever.task.activities import TaskChangeIssuerActivity
from opengever.task.response_syncer import BaseResponseSyncerReceiver
from opengever.task.response_syncer import BaseResponseSyncerSender
from opengever.task.response_syncer import ResponseSyncerSenderException
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class IssuerChangeResponseSyncerSender(BaseResponseSyncerSender):

    TARGET_SYNC_VIEW_NAME = '@@sync-task-issuer-change-response'

    def get_related_tasks_to_sync(self, transition):
        if not self._is_synced_transition(transition):
            return []

        tasks = super(IssuerChangeResponseSyncerSender, self).get_related_tasks_to_sync(
            transition)

        # Skip forwardings. Issuer changes should never be synced to the
        # predecessor forwarding, because a forwarding predecessor
        # is always closed and stored in the yearfolder.
        return [task for task in tasks if not task.is_forwarding]

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException(
            'Could not transfer issuer for task on remote '
            'admin unit {} ({})'.format(
                task.admin_unit_id,
                task.physical_path))

    def _is_synced_transition(self, transition):
        return transition in [
            'task-transition-change-issuer',
        ]


class IssuerChangeResponseSyncerReceiver(BaseResponseSyncerReceiver):
    """This view receives a @@sync-task-issuer-change-response request from
    another admin unit after the issuer was changed on a successor or
    predecessor task.
    """

    def __call__(self):
        self._check_internal_request()

        # This is a pseudo-transition. It's not an actual workflow transition,
        # but just a translated string that is used to make it look like a
        # state transition in the response timeline of the task.
        transition = self.request.get('transition')
        new_issuer = self.request.get('new_issuer')
        text = self.request.get('text')

        if self._is_already_done(transition, text):
            return ok_response(self.request)

        self._update(transition, new_issuer, text)
        return ok_response(self.request)

    def _update(self, transition, new_issuer, text):
        """Updates the current task with the received data (new issuer).
        """
        self.context.clear_reminder(self.context.issuer)

        changes = [(ITask['issuer'], new_issuer)]

        issuer_response = add_simple_response(
            self.context, transition=transition,
            text=text, field_changes=changes,
            supress_events=True)

        self.context.issuer = new_issuer
        notify(ObjectModifiedEvent(self.context))
        TaskChangeIssuerActivity(self.context, self.context.REQUEST, issuer_response).record()

        return issuer_response
