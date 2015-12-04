from AccessControl import getSecurityManager
from five import grok
from opengever.base.casauth import get_cas_portal_url
from opengever.base.casauth import is_cas_auth_enabled
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface


class LogoutOverlay(grok.View):
    """This view shows all documents checked out by the logged in user
    """
    grok.context(Interface)
    grok.name('logout_overlay')
    grok.require('zope2.View')
    items = []

    @property
    def redirect_url(self):
        if is_cas_auth_enabled():
            return '{}/logout'.format(get_cas_portal_url())
        else:
            portal_url_tool = getToolByName(self.context, 'portal_url')
            return '{}/logout'.format(portal_url_tool())

    def get_checkedout_documents(self):
        """ Return all documents checked out by the logged in user
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        user_id = getSecurityManager().getUser().getId()
        return catalog(checked_out=user_id)

    def update(self):
        self.items = self.get_checkedout_documents()

    def render(self):
        if not self.items:
            return "empty:%s" % self.redirect_url

        return ViewPageTemplateFile('templates/logout_overlay.pt')(self)
