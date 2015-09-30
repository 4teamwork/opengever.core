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
        for watching in resource.watchings:
            watchers[watching.watcher.user_id] = watching.roles

        return json.dumps(watchers)
