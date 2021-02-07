from App.config import getConfiguration
from opengever.base.monkey.patching import MonkeyPatch
from plone.session.plugins.session import cookie_expiration_date
import binascii


class PatchSessionCookie(MonkeyPatch):
    """Set session authentication cookie with SameSite=Lax flag"""

    def __call__(self):

        def _setCookie(self, cookie, response):
            cookie = binascii.b2a_base64(cookie).rstrip()
            # disable secure cookie in development mode, to ease local testing
            if getConfiguration().debug_mode:
                secure = False
            else:
                secure = self.secure
            options = dict(path=self.path, secure=secure, http_only=True)
            if self.cookie_domain:
                options['domain'] = self.cookie_domain
            if self.cookie_lifetime:
                options['expires'] = cookie_expiration_date(self.cookie_lifetime)
            options['same_site'] = 'Lax'
            response.setCookie(self.cookie_name, cookie, **options)

        from plone.session.plugins.session import SessionPlugin
        self.patch_refs(SessionPlugin, "_setCookie", _setCookie)
