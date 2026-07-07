from AccessControl import Unauthorized
from OFS.CopySupport import CopyError
from OFS.CopySupport import ResourceLockedError
from opengever.base.security import run_as_user
from opengever.bgtasks.task import BaseBackgroundTask
from opengever.bgtasks.task import register_task_type
from plone import api
import logging


logger = logging.getLogger('opengever.bgtasks')

TASK_TYPE = u'move-objects'


def paste_clipboard(destination, clipboard):
    """Paste a `manage_cutObjects()` clipboard into `destination`.
    """
    destination.manage_pasteObjects(cb_copy_data=clipboard)


class MoveObjectsTask(BaseBackgroundTask):

    task_type = TASK_TYPE

    def execute(self, task, commit_checkpoint):
        args = self.get_arguments(task)
        destination_uid = args.get(u'destination_uid')
        clipboard = args.get(u'clipboard')
        user_id = args.get(u'user_id')

        if not destination_uid or not clipboard or not user_id:
            logger.warning(
                u'Missing destination_uid, clipboard or user_id, skipping '
                u'move_objects')
            return

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog.unrestrictedSearchResults(UID=destination_uid)
        if not results:
            logger.warning(
                u'Destination %s not found in catalog, skipping '
                u'move_objects' % destination_uid)
            return

        try:
            destination = results[0]._unrestrictedGetObject()
        except Exception:
            logger.warning(
                u'Could not retrieve destination %s, skipping '
                u'move_objects' % destination_uid)
            return

        if destination is None:
            logger.warning(
                u'getObject() returned None for %s, skipping '
                u'move_objects' % destination_uid)
            return

        member = api.user.get(userid=user_id)
        real_user = member.getUser() if member is not None else None
        if real_user is None:
            # Never fall through to pasting as the worker's own (system)
            # user - that would bypass manage_pasteObjects's destination
            # permission check entirely.
            logger.warning(
                u'Queuing user %s could not be resolved, skipping '
                u'move_objects' % user_id)
            return

        real_user = real_user.__of__(api.portal.get().acl_users)

        with run_as_user(real_user):
            try:
                paste_clipboard(destination, clipboard)
            except (ValueError, CopyError, ResourceLockedError,
                    Unauthorized) as exc:
                # These are expected, non-retryable paste-time failures
                # (e.g. pasting a checked-out document, or the queuing user
                # lacking Add/access permission at the destination or
                # source). Retrying would not help and would only generate
                # noisy Sentry reports for conditions that are deliberately
                # not reported when raised synchronously.
                logger.warning(
                    u'Paste into %s failed, skipping move_objects: %s' % (
                        destination_uid, exc))


register_task_type(TASK_TYPE, MoveObjectsTask)
