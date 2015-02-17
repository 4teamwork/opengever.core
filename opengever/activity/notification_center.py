from opengever.activity import Activity
from opengever.activity import Notification
from opengever.activity import Resource
from opengever.activity import Session
from opengever.activity import Watcher


class NotificationCenter(object):
    """API Notification center.
    Splitted completly from plone to rise testability.
    """

    def add_resource(self, oguid):
        resource = Resource(oguid=oguid)
        Session.add(resource)
        return resource

    def fetch_resource(self, oguid):
        """Returns a resource by it's Oguid object or None when it does
        not exist.
        """
        return Resource.query.get_by_oguid(oguid)

    def add_watcher(self, user_id):
        watcher = Watcher(user_id=user_id)
        Session.add(watcher)
        return watcher

    def fetch_watcher(self, user_id):
        return Watcher.query.get_by_userid(user_id)

    def add_watcher_to_resource(self, oguid, userid):
        resource = self.fetch_resource(oguid)
        if not resource:
            resource = self.add_resource(oguid)

        resource.add_watcher(userid)

    def remove_watcher_from_resource(self, oguid, userid):
        watcher = self.fetch_watcher(userid)
        resource = self.fetch_resource(oguid)

        if watcher and resource:
            resource.remove_watcher(watcher)

    def get_watchers(self, oguid):
        resource = Resource.query.get_by_oguid(oguid)
        if not resource:
            return []

        return resource.watchers

    def add_activity(self, oguid, kind, title, summary, actor_id, description=u''):
        resource = self.fetch_resource(oguid)

        if not resource:
            resource = self.add_resource(oguid)

        activity = Activity(resource=resource, kind=kind,
                            title=title, summary=summary,
                            actor_id=actor_id, description=description)
        Session.add(activity)

        activity.notify()

        return activity

    def get_users_notifications(self, userid, only_unread=False, limit=None):
        query = Notification.query.by_user(userid)
        if only_unread:
            query = query.filter(Notification.read == False)

        return query.limit(limit).all()

    def mark_notification_as_read(self, notification_id):
        notification = Notification.get(notification_id)
        notification.read = True
