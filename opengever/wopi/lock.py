from AccessControl import getSecurityManager
from plone.locking.interfaces import IRefreshableLockable
from plone.locking.interfaces import STEALABLE_LOCK
from webdav.LockItem import LockItem

WOPI_MARKER = 'WOPI_'


def create_lock(obj, token):
    """Create a lock with a custom token."""
    user = getSecurityManager().getUser()
    token = WOPI_MARKER + token
    lock = LockItem(user, depth=0, timeout=1800, token=token)
    obj.wl_setLock(token, lock)
    lockable = IRefreshableLockable(obj, None)
    locks = lockable._locks()
    locks[STEALABLE_LOCK.__name__] = dict(
        type=STEALABLE_LOCK, token=token)


def get_lock_token(obj):
    lockable = IRefreshableLockable(obj, None)
    if lockable is not None:
        lock_info = lockable.lock_info()
        if lock_info:
            token = lock_info[0]['token']
            if token.startswith(WOPI_MARKER):
                return token[len(WOPI_MARKER):]


def unlock(obj):
    lockable = IRefreshableLockable(obj, None)
    if lockable is not None:
        lockable.unlock()


def refresh_lock(obj):
    lockable = IRefreshableLockable(obj, None)
    if lockable is not None:
        lockable.refresh_lock()
