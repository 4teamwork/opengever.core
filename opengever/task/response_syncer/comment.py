from opengever.task.response_syncer import BaseResponseSyncerReceiver
from opengever.task.response_syncer import BaseResponseSyncerSender
from opengever.task.response_syncer import ResponseSyncerSenderException


class CommentResponseSyncerSender(BaseResponseSyncerSender):

    TARGET_SYNC_VIEW_NAME = '@@sync-task-comment-response'

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException(
            'Could not add comment on task on remote admin unit {} ({})'.format(
                task.admin_unit_id,
                task.physical_path))

    def get_related_tasks_to_sync(self, transition):
        tasks = super(CommentResponseSyncerSender, self).get_related_tasks_to_sync(
            transition)

        # Skip forwardings. Comments should never be synced to the
        # successor forwarding, because a forwarding predecessor
        # is allways closed and stored in the yearfolder.
        return [task for task in tasks if not task.is_forwarding]


class CommentResponseSyncerReceiver(BaseResponseSyncerReceiver):
    """This view receives a sync-task-comment-response request from another
    client after new comments have been added to a successor or predecessor.
    """
