from opengever.base.monkey.patching import MonkeyPatch
from opengever.readonly import is_in_readonly_mode
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
