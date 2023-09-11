from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import create_session
from opengever.document.behaviors import IBaseDocument
from opengever.locking.interfaces import ISQLLockable
from opengever.locking.model import Lock
from plone import api
from plone.locking.interfaces import INonStealableLock
from plone.locking.interfaces import IRefreshableLockable
from plone.locking.interfaces import STEALABLE_LOCK
from plone.locking.lockable import TTWLockable
from sqlalchemy import inspect
from zope.component import adapts
from zope.interface import implements


class GeverLockable(TTWLockable):
    def lock(self, *args, **kwargs):
        super(GeverLockable, self).lock(*args, **kwargs)
        self.reindex()

    def unlock(self, *args, **kwargs):
        super(GeverLockable, self).unlock(*args, **kwargs)
        self.reindex()

    def clear_locks(self):
        super(GeverLockable, self).clear_locks()
        self.reindex()

    def reindex(self):
        if IBaseDocument.providedBy(self.context):
            self.context.reindexObject(
                idxs=['is_locked_by_copy_to_workspace', 'UID'])


class SQLLockable(object):
    """An entity that is being locked through-the-web.
    """

    implements(IRefreshableLockable)
    adapts(ISQLLockable)

    def __init__(self, context):
        self.context = context
        self.model = context.model
        self.session = create_session()

    @property
    def object_type(self):
        return self.model.__class__.__name__

    @property
    def object_id(self):
        return '-'.join([str(_id) for _id in inspect(self.model).identity])

    @property
    def is_stealable(self):
        return True

    def searialize_lock_type(self, lock_type):
        return lock_type.__name__

    def desearialize_lock_type(self, lock_type):
        if lock_type != STEALABLE_LOCK.__name__:
            raise NotImplementedError

        return STEALABLE_LOCK

    def lock(self, lock_type=STEALABLE_LOCK, children=False):
        """Lock the object using the given key.

        If children is True, child objects will be locked as well.
        """

        self.clear_expired_locks()

        lock = Lock(object_id=self.object_id,
                    object_type=self.object_type,
                    creator=api.user.get_current().getId(),
                    lock_type=self.searialize_lock_type(lock_type))
        self.session.add(lock)

    def refresh_lock(self, lock_type=STEALABLE_LOCK):
        if not self.locked():
            return

        lock = self._get_lock(lock_type)
        lock.time = utcnow_tz_aware()

    def unlock(self, lock_type=STEALABLE_LOCK, stealable_only=True):
        """Unlock the object using the given key.

        If stealable_only is true, the operation will only have an effect on
        objects that are stealable(). Thus, non-stealable locks will need
        to pass stealable_only=False to actually get unlocked.
        """
        if not self.locked():
            return

        if not stealable_only or self.stealable(lock_type):
            Lock.query.filter_by(
                object_type=self.object_type,
                object_id=self.object_id,
                lock_type=self.searialize_lock_type(lock_type)).delete()

    def clear_expired_locks(self):
        locks = Lock.query.invalid_locks()
        locks.delete()

    def clear_locks(self):
        """Clear all locks on the object
        """
        locks = Lock.query.filter_by(object_type=self.object_type,
                                     object_id=self.object_id)
        locks.delete()

    def locked(self):
        """It's True if the object is locked with any valid lock.
        """
        return Lock.query.valid_locks(
            self.object_type, self.object_id).count() > 0

    def can_safely_unlock(self, lock_type=STEALABLE_LOCK):
        """Determine if the current user can safely attempt to unlock the
        object.

        That means:

         - lock_type.user_unlockable is True; and

         - the object is not locked; or
         - the object is only locked with the given lock_type, for the
           current user;
        """

        if not lock_type.user_unlockable:
            return False

        if not self.locked():
            return True

        lock = self._get_lock(lock_type)
        if lock.creator == api.user.get_current().getId():
            return True

        return False

    def stealable(self, lock_type=STEALABLE_LOCK):
        """Copied from plone.locking.lockable.TTWLockable

        Find out if the lock can be stolen.
        This means:

         - the lock type is stealable; and

         - the object is not marked with INonStealableLock; or
         - can_safely_unlock() is true.
        """

        # If the lock type is not stealable ever, return False
        if not lock_type.stealable:
            return False
        # Can't steal locks of a different type
        for lock in self.lock_info():
            if (
                not hasattr(lock['type'], '__name__')
                or lock['type'].__name__ != lock_type.__name__
            ):
                return False
        # The lock type is stealable, and the object is not marked as
        # non-stelaable, so return True
        if not INonStealableLock.providedBy(self.context):
            return True
        # Lock type is stealable, object is not stealable, but return True
        # anyway if we can safely unlock this object (e.g. we are the owner)
        return self.can_safely_unlock(lock_type)

    def lock_info(self):
        """Get information about locks on object.

        Returns a list containing the following dict for each valid lock:

         - creator : the username of the lock creator
         - time    : the time at which the lock was acquired
         - token   : the underlying lock token
         - type    : the type of lock
        """
        infos = []

        locks = Lock.query.valid_locks(self.object_type, self.object_id)
        for lock in locks:
            infos.append({'creator': lock.creator,
                          'time': lock.time,
                          'token': lock.token,
                          'type': self.desearialize_lock_type(lock.lock_type)})

        return infos

    def _get_lock(self, lock_type):
        query = Lock.query.valid_locks(self.object_type, self.object_id)
        query = query.filter_by(lock_type=self.searialize_lock_type(lock_type))
        return query.first()
