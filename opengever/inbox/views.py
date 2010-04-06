from five import grok
from zope.interface import Interface

class AccessInboxAllowed(grok.CodeView):
    grok.context(Interface)
    grok.name('access-inbox-allowed')

    def render(self):
        portal = self.context.portal_url.getPortalObject()
        eingangskorb = portal.eingangskorb
        member = self.context.portal_membership.getAuthenticatedMember()
        try:
            member.checkPermission
        except:
            return False
        else:
            return member.checkPermission('View', eingangskorb)
    
