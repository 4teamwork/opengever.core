from Acquisition import aq_parent
from opengever.activity.model import Resource
from opengever.base.interfaces import IDeleter
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from plone import api
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from zExceptions import Forbidden
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IDeleter)
@adapter(Interface)
class BaseContentDeleter(object):
    """Deleter adapter used for deleting objects over the REST-API
    """

    permission = "Delete objects"

    def __init__(self, context):
        self.context = context

    def delete(self):
        self.verify_may_delete()
        self.cleanup_resources()
        self._delete()

    def cleanup_resources(self):
        oguid = Oguid.for_object(self.context)
        resource = Resource.query.get_by_oguid(oguid)
        if resource:
            session = create_session()
            for subscription in resource.subscriptions:
                session.delete(subscription)
            session.delete(resource)

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

    def is_delete_allowed(self):
        try:
            self.verify_may_delete()
            return True
        except Forbidden:
            return False
