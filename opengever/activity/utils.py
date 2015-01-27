from opengever.activity.notification_center import NotificationCenter
from opengever.base.oguid import Oguid
from plone import api


def notification_center():
    return PloneNotificationCenter()


class PloneNotificationCenter(NotificationCenter):
    """The PloneNotificationCenter is a wrapper of the NotificationCenter,
    which provides some helper methods for easier access.
    """

    def add_watcher_to_resource(self, obj, userid):
        oguid = Oguid.for_object(obj)
        super(PloneNotificationCenter, self).add_watcher_to_resource(oguid, userid)

    def add_activity(self, obj, kind, title, summary, actor_id, description=u''):
        oguid = Oguid.for_object(obj)

        return super(PloneNotificationCenter, self).add_activity(
            oguid, kind, title, summary, actor_id, description=description)

    def get_watchers(self, obj):
        oguid = Oguid.for_object(obj)
        return super(PloneNotificationCenter, self).get_watchers(oguid)

    def get_current_users_notifications(self, only_unread=False, limit=None):
        return super(PloneNotificationCenter, self).get_users_notifications(
            api.user.get_current().getId(),
            only_unread=only_unread,
            limit=limit)
