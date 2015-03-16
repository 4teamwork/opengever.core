from opengever.activity.center import DisabledNotificationCenter
from opengever.activity.center import PloneNotificationCenter
from opengever.activity.utils import is_activity_feature_enabled
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.activity")


def notification_center():
    if not is_activity_feature_enabled():
        return DisabledNotificationCenter()

    return PloneNotificationCenter()
