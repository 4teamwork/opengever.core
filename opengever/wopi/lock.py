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


def validate_lock(server_token, client_token, strict=True):
    """Return True if a client's lock token is valid, False otherwise.

    Usually this means that the lock token strings must match exactly.
    However, for some put_file operations the MS WOPI client does actually
    send incomplete tokens, which still need to be accepted.

    We've so far only seen this for the put_file operation, and in these
    two specific variants:
    - The client token is a substring of the server_token
    - The client token looks like JSON, and contains a subset of the key/value
      pairs present in the server_token (with keys in the same order).

    When invoked with strict=False, we also consider these two partial
    matches valid.
    """
    if strict:
        return server_token == client_token

    return any((
        server_token == client_token,
        '}' in client_token and client_token[:-1] in server_token,
        client_token in server_token,
    ))
