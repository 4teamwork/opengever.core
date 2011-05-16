from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from opengever.inbox.inbox import IInbox
import json


class InboxGroupAsJSONView(grok.CodeView):
    """Displays the Inboxgroup of this client"""
    grok.context(IPloneSiteRoot)
    grok.name('tentacle-inbox-group-json')

    def render(self):
        # returns the configigured inbox_group of this client
        portal = self.context.portal_url.getPortalObject()
        inbox = portal.get('eingangskorb')
        repr_ = IInbox(inbox)
        return json.dumps(getattr(repr_, 'inbox_group'))
