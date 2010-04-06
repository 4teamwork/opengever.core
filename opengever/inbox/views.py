from five import grok
from zope.interface import Interface

class AccessInboxAllowed(grok.CodeView):
    grok.context(Interface)
    grok.name('access-inbox-allowed')

    def render(self):
        portal = self.context.portal_url.getPortalObject()
        journal = portal.journal
        member = self.context.portal_membership.getAuthenticatedMember()
        return member.checkPermission('View', journal)
    
