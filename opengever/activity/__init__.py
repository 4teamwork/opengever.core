from opengever.activity.center import DisabledNotificationCenter
from opengever.activity.center import PloneNotificationCenter
from opengever.activity.interfaces import IActivitySettings
from opengever.activity.mail import PloneNotificationMailer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface


_ = MessageFactory("opengever.activity")


def is_activity_feature_enabled():
    try:
        registry = getUtility(IRegistry)
        return registry.forInterface(IActivitySettings).is_feature_enabled

    except KeyError, AttributeError:
        return False


def notification_center():
    if not is_activity_feature_enabled():
        return DisabledNotificationCenter()

    return PloneNotificationCenter(dispatchers=[PloneNotificationMailer()])
