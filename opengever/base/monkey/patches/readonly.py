from opengever.base.monkey.patching import MonkeyPatch
from plone.protect import subscribers
from Products.PlonePAS.tools.membership import MembershipTool
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from zope.component import adapter
from zope.component.hooks import getSite


class PatchMembershipToolSetLoginTimes(MonkeyPatch):

    def __call__(self):

        def setLoginTimes(self):
            site = getSite()
            conn = site._p_jar
            if conn.isReadOnly():
                return False

            return original_setLoginTimes(self)

        locals()['__patch_refs__'] = False
        original_setLoginTimes = MembershipTool.setLoginTimes

        self.patch_refs(MembershipTool, 'setLoginTimes', setLoginTimes)


class PatchMembershipToolCreateMemberarea(MonkeyPatch):

    def __call__(self):

        def createMemberarea(self):
            site = getSite()
            conn = site._p_jar
            if conn.isReadOnly():
                return

            return original_createMemberarea(self)

        locals()['__patch_refs__'] = False
        original_createMemberarea = MembershipTool.createMemberarea

        self.patch_refs(MembershipTool, 'createMemberarea', createMemberarea)
        self.patch_refs(MembershipTool, 'createMemberArea', createMemberarea)


class PatchPloneProtectOnUserLogsIn(MonkeyPatch):

    def __call__(self):

        @adapter(IUserLoggedInEvent)
        def onUserLogsIn(self):
            site = getSite()
            conn = site._p_jar
            if conn.isReadOnly():
                return

            return original_onUserLogsIn(self)

        locals()['__patch_refs__'] = False
        original_onUserLogsIn = subscribers.onUserLogsIn

        self.patch_refs(subscribers, 'onUserLogsIn', onUserLogsIn)
