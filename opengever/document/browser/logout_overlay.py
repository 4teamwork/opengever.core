from AccessControl import getSecurityManager
from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import is_cas_auth_enabled
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class LogoutOverlay(BrowserView):
    """This view shows all documents checked out by the logged in user
    """
    items = []

    @property
    def redirect_url(self):
        if is_cas_auth_enabled():
            # Single-Logout via CAS server
            return '{}/logout'.format(get_cas_server_url())
        else:
            # Logout via Plone PAS
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

    def __call__(self):
        self.update()
        if not self.items:
            return "empty:%s" % self.redirect_url

        return ViewPageTemplateFile('templates/logout_overlay.pt')(self)
