from plone.locking.interfaces import LockType
from plone.locking.interfaces import MAX_TIMEOUT

# TODO: Rename sys.lock to meeting.protocol.lock
LOCK_TYPE_SYS_LOCK = u'sys.lock'

SYS_LOCK = LockType(LOCK_TYPE_SYS_LOCK, stealable=True, user_unlockable=True,
                    timeout=MAX_TIMEOUT)
