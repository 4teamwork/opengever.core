from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.locking.lock import LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK
from plone import api
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import INonStealableLock
from plone.locking.interfaces import STEALABLE_LOCK
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.services.locking.locking import lock_info
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides
from zope.security import checkPermission


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class Lock(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'lock': {
                '@id': '/'.join((self.context.absolute_url(), '@lock')),
            },
        }
        if expand:
            result['lock'].update(lock_info(self.context) or {})
        return result


class Unlock(Service):
    """Unlock an object"""

    def get_lock_type(self, info):
        data = json_body(self.request)
        lock_type_name = data.get('lock_type', STEALABLE_LOCK.__name__)
        for lock in info:
            if lock['type'].__name__ == lock_type_name:
                return lock['type']
        return STEALABLE_LOCK

    def reply(self):
        lockable = ILockable(self.context)
        info = lockable.lock_info()
        lock_type = self.get_lock_type(info)

        if can_unlock_obj(self.context, lock_type):
            lockable.unlock(lock_type)

            if INonStealableLock.providedBy(self.context):
                noLongerProvides(self.context, INonStealableLock)

            # Disable CSRF protection
            alsoProvides(self.request, IDisableCSRFProtection)

        return lock_info(self.context)


def can_unlock_obj(obj, lock_type):
    if "Manager" in api.user.get_roles():
        return True
    if not checkPermission('cmf.ModifyPortalContent', obj):
        return False
    lockable = ILockable(obj)
    if not lock_type.user_unlockable:
        return False

    info = lockable.lock_info()
    # There is no lock, so return True
    if len(info) == 0:
        return True

    userid = api.user.get_current().getId() or None
    for l in info:
        # There is another lock of a different type
        if not hasattr(l['type'], '__name__') or \
           l['type'].__name__ != lock_type.__name__:
            return False
        # The lock is in fact held by the current user
        if l['creator'] == userid:
            return True
        # workspace lock can also be unlocked by users who have not created the lock
        if lock_type.__name__ == LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK:
            return True
    return False
