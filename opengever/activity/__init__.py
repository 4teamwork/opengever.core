from opengever.activity.center import DisabledNotificationCenter
from opengever.activity.center import PloneNotificationCenter
from opengever.activity.interfaces import IActivitySettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.activity")


def is_activity_feature_enabled():
    registry = getUtility(IRegistry)
    return registry.forInterface(IActivitySettings).is_feature_enabled


def notification_center():
    if not is_activity_feature_enabled():
        return DisabledNotificationCenter()

    return PloneNotificationCenter()
