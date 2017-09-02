from opengever.activity import notification_center
from Products.Five import BrowserView
import json


class Watchers(BrowserView):
    """Maintenance/Debugging view, which shows watchers of the current object.
    """

    def render(self):
        resource = notification_center().fetch_resource(self.context)
        watchers = {}
        for subscription in resource.subscriptions:
            watchers.setdefault(subscription.watcher.actorid, []).append(
                subscription.role)

        return json.dumps(watchers)
