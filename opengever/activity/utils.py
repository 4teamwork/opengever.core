from opengever.activity.notification_center import NotificationCenter
from opengever.globalindex.oguid import Oguid


def notification_center():
    return PloneNotificationCenter()


class PloneNotificationCenter(NotificationCenter):
    """The PloneNotificationCenter is a wrapper of the NotificationCenter,
    which provides some helper methods for easier access.
    """

    def add_watcher_to_resource(self, obj, userid):
        oguid = Oguid.for_object(obj)
        super(PloneNotificationCenter, self).add_watcher_to_resource(oguid, userid)

    def add_acitivity(self, obj, kind, title, actor_id, description=u''):
        oguid = Oguid.for_object(obj)

        return super(PloneNotificationCenter, self).add_acitivity(
            oguid, kind, title, actor_id, description=description)

    def get_watchers(self, obj):
        oguid = Oguid.for_object(obj)
        return super(PloneNotificationCenter, self).get_watchers(oguid)
