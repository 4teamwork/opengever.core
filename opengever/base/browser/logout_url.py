from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import is_cas_auth_enabled
from plone import api
from Products.Five import BrowserView


class LogoutURL(BrowserView):
    """This view shows all documents checked out by the logged in user
    """
    items = []

    def __call__(self):

        if is_cas_auth_enabled():
            # Single-Logout via CAS server
            return '{}/logout'.format(get_cas_server_url())
        else:
            # Logout via Plone PAS
            return '{}/logout'.format(api.portal.get().absolute_url())
