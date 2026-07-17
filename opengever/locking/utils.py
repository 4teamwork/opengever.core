from Acquisition import aq_parent
from opengever.locking.lock import MOVE_LOCK
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import ITTWLockable
from Products.CMFCore.interfaces import IContentish


def has_move_lock(obj):
    while IContentish.providedBy(obj):
        if ITTWLockable.providedBy(obj):
            info = ILockable(obj).lock_info()
            if info and any([i['type'] == MOVE_LOCK for i in info]):
                return True
        obj = aq_parent(obj)
    return False
