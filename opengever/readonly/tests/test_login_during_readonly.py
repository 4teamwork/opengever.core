from AccessControl import getSecurityManager
from DateTime import DateTime
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
from plone import api
from plone.app.contentrules import handlers as contentrules_handlers
from plone.app.testing import TEST_USER_ID
from plone.protect import subscribers as plone_protect_subscribers
from Products.PlonePAS.events import UserLoggedInEvent
import transaction


class TestLoginDuringReadOnlyMode(FunctionalTestCase):

    @browsing
    def test_set_login_times_doesnt_prevent_login_during_readonly(self, browser):
        membership_tool = api.portal.get_tool('portal_membership')

        with ZODBStorageInReadonlyMode():
            browser.login()
            membership_tool.setLoginTimes()
            transaction.commit()

        member = membership_tool.getAuthenticatedMember()
        self.assertEqual(TEST_USER_ID, member.getId())
        self.assertEqual(DateTime('2000/01/01'), member.getProperty('last_login_time'))

    @browsing
    def test_contentrules_handler_doesnt_prevent_login_during_readonly(self, browser):
        membership_tool = api.portal.get_tool('portal_membership')

        with ZODBStorageInReadonlyMode():
            browser.login()

            user = getSecurityManager().getUser()
            event = UserLoggedInEvent(user)
            contentrules_handlers.user_logged_in(event)

            transaction.commit()

        member = membership_tool.getAuthenticatedMember()
        self.assertEqual(TEST_USER_ID, member.getId())

    @browsing
    def test_plone_protect_doesnt_prevent_login_during_readonly(self, browser):
        membership_tool = api.portal.get_tool('portal_membership')

        with ZODBStorageInReadonlyMode():
            browser.login()

            user = getSecurityManager().getUser()
            event = UserLoggedInEvent(user)
            plone_protect_subscribers.onUserLogsIn(event)

            transaction.commit()

        member = membership_tool.getAuthenticatedMember()
        self.assertEqual(TEST_USER_ID, member.getId())
