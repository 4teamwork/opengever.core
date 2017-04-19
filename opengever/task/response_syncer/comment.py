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


class CommentResponseSyncerReceiver(BaseResponseSyncerReceiver):
    """This view receives a sync-task-comment-response request from another
    client after new comments have been added to a successor or predecessor.
    """
