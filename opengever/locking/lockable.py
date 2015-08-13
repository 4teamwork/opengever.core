from opengever.base.model import create_session
from opengever.locking.interfaces import ISQLLockable
from opengever.locking.model import Lock
from opengever.locking.model.locks import utcnow_tz_aware
from plone import api
from plone.locking.interfaces import INonStealableLock
from plone.locking.interfaces import IRefreshableLockable
from plone.locking.interfaces import STEALABLE_LOCK
from zope.component import adapts
from zope.interface import implements


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
        # XXX should use a general id getter (via primary key)
        return self.model.meeting_id

    @property
    def is_stealable(self):
        return True

    def searialize_lock_type(self, lock_type):
        return lock_type.__name__

    def lock(self, lock_type=STEALABLE_LOCK, children=False):
        """Lock the object using the given key.

        If children is True, child objects will be locked as well.
        """

        lock = Lock(object_id=self.object_id,
                    object_type=self.object_type,
                    creator=api.user.get_current().getId(),
                    lock_type=self.searialize_lock_type(lock_type))

        self.session.add(lock)

        self.clear_expired_locks()

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

        if not self.locked():
            return True

        lock = self._get_lock(lock_type)
        if lock.creator == api.user.get_current().getId():
            return True

        return False

    def stealable(self, lock_type=STEALABLE_LOCK):
        """Find out if the lock can be stolen.

        This means:

         - the lock type is stealable; and

         - the object is not marked with INonStealableLock; or
         - can_safely_unlock() is true.

        """

        if not lock_type.stealable:
            return False
        if not INonStealableLock.providedBy(self.context):
            return True

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
                          'type': lock.lock_type})

        return infos

    def _get_lock(self, lock_type):
        query = Lock.query.valid_locks(self.object_type, self.object_id)
        query = query.filter_by(lock_type=self.searialize_lock_type(lock_type))
        return query.first()
