from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.base.monkey.patching import MonkeyPatch
from opengever.readonly import is_in_readonly_mode
from plone.app.contentrules import handlers as contentrules_handlers
from plone.protect import subscribers as plone_protect_subscribers
from plone.protect.interfaces import IDisableCSRFProtection
from Products.PlonePAS.tools.membership import MembershipTool
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import alsoProvides


class PatchMembershipToolSetLoginTimes(MonkeyPatch):
    """In read-only mode, allow login of existing users without updating
    their last login times (which would cause a write).

    The return value of False signals that this is not the user's very
    first login.
    """

    def __call__(self):

        def setLoginTimes(self):
            if is_in_readonly_mode():
                return False

            return original_setLoginTimes(self)

        locals()['__patch_refs__'] = False
        original_setLoginTimes = MembershipTool.setLoginTimes

        self.patch_refs(MembershipTool, 'setLoginTimes', setLoginTimes)


class PatchCASAuthSetLoginTimes(MonkeyPatch):
    """Same for ftw.casauth - don't update last login times in readonly mode.
    """

    def __call__(self):

        def set_login_times(self, member):
            if is_in_readonly_mode():
                return False

            return original_set_login_times(self, member)

        locals()['__patch_refs__'] = False
        original_set_login_times = CASAuthenticationPlugin.set_login_times

        self.patch_refs(CASAuthenticationPlugin, 'set_login_times', set_login_times)


class PatchContentRulesHandlerOnLogin(MonkeyPatch):
    """In read-only mode, don't execute the plone.app.contentrules handler
    on the UserLoggedInEvent. This handler may in some cases initialize some
    settings on the Plone site, and would therefore cause writes.
    """

    def __call__(self):

        def user_logged_in(event):
            if is_in_readonly_mode():
                return

            return original_user_logged_in(event)

        locals()['__patch_refs__'] = False
        original_user_logged_in = contentrules_handlers.user_logged_in

        self.patch_refs(contentrules_handlers, 'user_logged_in', user_logged_in)


class PatchPloneProtectOnUserLogsIn(MonkeyPatch):
    """In read-only mode, prevent plone.protect from rotating the key ring on
    login, which may cause DB writes and prevent the user from logging in.
    """

    def __call__(self):

        @adapter(IUserLoggedInEvent)
        def onUserLogsIn(event):
            if is_in_readonly_mode():
                # disable csrf protection on login requests
                req = getRequest()
                alsoProvides(req, IDisableCSRFProtection)
                return

            return original_onUserLogsIn(event)

        locals()['__patch_refs__'] = False
        original_onUserLogsIn = plone_protect_subscribers.onUserLogsIn

        self.patch_refs(plone_protect_subscribers, 'onUserLogsIn', onUserLogsIn)


class PatchMembershipToolCreateMemberarea(MonkeyPatch):
    """In read-only mode, don't create a user's member area.

    This would cause a DB write and therefore is not supported while readonly
    mode is active.
    """

    def __call__(self):

        def createMemberarea(self, *args, **kwargs):
            if is_in_readonly_mode():
                return

            return original_createMemberarea(self, *args, **kwargs)

        locals()['__patch_refs__'] = False
        original_createMemberarea = MembershipTool.createMemberarea

        # Patch both spellings (API change in CMF)
        self.patch_refs(MembershipTool, 'createMemberarea', createMemberarea)
        self.patch_refs(MembershipTool, 'createMemberArea', createMemberarea)
