from opengever.base.monkey.patching import MonkeyPatch
from opengever.readonly import is_in_readonly_mode
from plone.app.contentrules import handlers as contentrules_handlers
from Products.PlonePAS.tools.membership import MembershipTool


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
