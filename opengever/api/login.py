from plone.restapi.deserializer import json_body
from plone.restapi.services.auth.login import Login
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from zope.interface import alsoProvides
import plone.protect.interfaces
import six


# Copied from plone.restapi.services.auth.login.py
# Customized to allow cookie-based authentication in addition to JWT
class GeverLogin(Login):
    def reply(self):
        data = json_body(self.request)
        if "login" not in data or "password" not in data:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="Missing credentials",
                    message="Login and password must be provided in body.",
                )
            )

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        set_cookie = data.get('set_cookie', False)
        userid = data["login"]
        password = data["password"]
        if six.PY2:
            userid = userid.encode("utf8")
            password = password.encode("utf8")
        uf = self._find_userfolder(userid)

        if uf is not None:
            if not set_cookie:
                plugins = uf._getOb("plugins")
                authenticators = plugins.listPlugins(IAuthenticationPlugin)
                plugin = None
                for _id, authenticator in authenticators:
                    if authenticator.meta_type == "JWT Authentication Plugin":
                        plugin = authenticator
                        break

                if plugin is None:
                    self.request.response.setStatus(501)
                    return dict(
                        error=dict(
                            type="Login failed",
                            message="JWT authentication plugin not installed.",
                        )
                    )

            user = uf.authenticate(userid, password, self.request)
        else:
            user = None

        if not user:
            self.request.response.setStatus(401)
            return dict(
                error=dict(
                    type="Invalid credentials", message="Wrong login and/or password."
                )
            )

        if set_cookie:
            uf.updateCredentials(
                self.request, self.request.response, user.getUserName(), password)
            return {'userid': userid, 'fullname': user.getProperty('fullname')}
        else:
            payload = {}
            payload["fullname"] = user.getProperty("fullname")
            return {"token": plugin.create_token(user.getId(), data=payload)}
