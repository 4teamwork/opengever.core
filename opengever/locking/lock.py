from plone.locking.interfaces import LockType
from plone.locking.interfaces import MAX_TIMEOUT


SYS_LOCK = LockType(u'sys.lock', stealable=True, user_unlockable=True,
                    timeout=MAX_TIMEOUT)
