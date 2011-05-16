from five import grok
from zope.interface import Interface

class AccessInboxAllowed(grok.CodeView):
    """Checks if the User has enough permissions to view the Inbox.
    """
    grok.context(Interface)
    grok.name('access-inbox-allowed')

    def render(self):
        """Checks User permissions"""
        portal = self.context.portal_url.getPortalObject()
        eingangskorb = portal.eingangskorb
        member = self.context.portal_membership.getAuthenticatedMember()
        try:
            member.checkPermission
        except AttributeError:
            return False
        else:
            return member.checkPermission('View', eingangskorb)

