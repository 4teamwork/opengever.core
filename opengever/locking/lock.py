from plone.locking.interfaces import LockType
from plone.locking.interfaces import MAX_TIMEOUT


# TODO: Rename sys.lock to meeting.protocol.lock
LOCK_TYPE_SYS_LOCK = u'sys.lock'

SYS_LOCK = LockType(LOCK_TYPE_SYS_LOCK, stealable=True, user_unlockable=True,
                    timeout=MAX_TIMEOUT)


LOCK_TYPE_MEETING_SUBMITTED_LOCK = u'meeting.submitted.lock'
MEETING_SUBMITTED_LOCK = LockType(
    LOCK_TYPE_MEETING_SUBMITTED_LOCK,
    stealable=True, user_unlockable=True, timeout=MAX_TIMEOUT)


LOCK_TYPE_MEETING_EXCERPT_LOCK = u'meeting.excerpt.lock'
MEETING_EXCERPT_LOCK = LockType(
    LOCK_TYPE_MEETING_EXCERPT_LOCK,
    stealable=True, user_unlockable=True, timeout=MAX_TIMEOUT)


LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK = u'document.copied_to_workspace.lock'
COPIED_TO_WORKSPACE_LOCK = LockType(
    LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK,
    stealable=True, user_unlockable=True, timeout=MAX_TIMEOUT)
