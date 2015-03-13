from opengever.activity.interfaces import IActivitySettings
from opengever.activity.models.activity import Activity
from opengever.activity.models.notification import Notification
from opengever.activity.models.resource import Resource
from opengever.activity.models.watcher import Watcher
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.activity")


def is_activity_feature_enabled():
    registry = getUtility(IRegistry)
    return registry.forInterface(IActivitySettings).is_feature_enabled
