from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import is_cas_auth_enabled
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five import BrowserView


class LogoutView(BrowserView):
    """Log out current user, and redirect to CAS logout if necessary.

    Very loosely based on Products/CMFPlone/skins/plone_login/logout.cpy
    """

    def __call__(self):
        mt = getToolByName(self.context, 'portal_membership')
        mt.logoutUser(self.request)

        transaction_note('Logged out')

        if is_cas_auth_enabled():
            target_url = '{}/logout'.format(get_cas_server_url())
        else:
            target_url = '{}/logged_out'.format(api.portal.get().absolute_url())

        return self.request.RESPONSE.redirect(target_url)
