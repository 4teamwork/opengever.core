from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
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

        return ViewPageTemplateFile(
            './logout_overlay_templates/logout_overlay.pt')(self)
