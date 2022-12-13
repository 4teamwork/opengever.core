from Acquisition import aq_parent
from opengever.base.interfaces import IDeleter
from plone import api
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from zExceptions import Forbidden
from zope.interface import implementer


@implementer(IDeleter)
class BaseContentDeleter(object):
    """Deleter adapter used for deleting objects over the REST-API
    """

    permission = "Delete objects"

    def __init__(self, context):
        self.context = context

    def delete(self):
        self.verify_may_delete()
        self._delete()

    def _delete(self):
        parent = aq_parent(self.context)
        try:
            parent._delObject(self.context.getId())
        except LinkIntegrityNotificationException:
            pass

    def verify_may_delete(self, **kwargs):
        self.check_delete_permission()

    def check_delete_permission(self):
        if not api.user.has_permission(self.permission, obj=self.context):
            raise Forbidden()
