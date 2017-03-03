from five import grok
from opengever.activity import notification_center
from zope.interface import Interface
import json


class Watchers(grok.View):
    """Maintenance/Debugging view, which shows watchers of the current object.
    """
    grok.name('watchers')
    grok.context(Interface)
    grok.require('cmf.ManagePortal')

    def render(self):
        resource = notification_center().fetch_resource(self.context)
        watchers = {}
        for subscription in resource.subscriptions:
            watchers.setdefault(subscription.watcher.actorid, []).append(
                subscription.role)

        return json.dumps(watchers)
