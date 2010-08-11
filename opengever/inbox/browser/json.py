from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from opengever.inbox.inbox import IInbox
import simplejson


class InboxGroupAsJSONView(grok.CodeView):
    grok.context(IPloneSiteRoot)
    grok.name('tentacle-inbox-group-json')

    def render(self):
        # returns the configigured inbox_group of this client
        portal = self.context.portal_url.getPortalObject()
        inbox = portal.get('eingangskorb')
        repr = IInbox(inbox)
        return simplejson.dumps(getattr(repr, 'inbox_group'))
