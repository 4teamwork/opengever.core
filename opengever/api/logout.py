from Products.CMFCore.utils import getToolByName
from plone.restapi.services.auth.logout import Logout


class GeverLogout(Logout):
    """Log out current user by trying to invalidate the JWT and expiring
    his cookies (__ac and deployment specific cookie, e.g. __ac_fd).
    This is necessary because logout in the frontend should also log the user
    out of the backend.
    """

    def reply(self):
        # Handles logout by invalidating the JWT
        # This sets the response status accordingly if it fails
        resp = super(GeverLogout, self).reply()

        # Now we try to expire the user's cookies

        # We do not use logout of PAS here, as it redirects to logout view.
        pas = getToolByName(self.context, 'acl_users')
        pas.resetCredentials(self.request, self.request['RESPONSE'])

        # Also expire any __ac cookie that might have been issued by the
        # CookieAuthHelper on the Zope root (e.g. for zopemaster)
        self.request.response.expireCookie('__ac', path='/')

        # if either the JWT token was invalidated or any cookie was deleted
        # logout is considered successful, otherwise we return the error
        # from the JWT logout.
        for cookie_name, cookie in self.request.response.cookies.items():
            if cookie.get('value') == 'deleted' and cookie_name in self.request.cookies:
                self.request.response.setStatus(204)
                return
        return resp
