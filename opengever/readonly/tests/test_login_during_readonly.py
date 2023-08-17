from AccessControl import getSecurityManager
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from mock import patch
from opengever.testing import FunctionalTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
from plone import api
from plone.app.contentrules import handlers as contentrules_handlers
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.protect import subscribers as plone_protect_subscribers
from Products.PlonePAS.events import UserLoggedInEvent
import transaction


class TestLoginDuringReadOnlyMode(FunctionalTestCase):

    def create_private_root(self, membership_tool):
        # Create private root (the place where users' member folders reside)
        membership_tool.setMemberareaCreationFlag()
        private_root = create(Builder('private_root'))
        membership_tool.setMembersFolderById(private_root.id)
        membership_tool.setMemberAreaType('opengever.private.folder')

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

    @browsing
    def test_member_area_creation_doesnt_prevent_login_during_readonly(self, browser):
        membership_tool = api.portal.get_tool('portal_membership')
        self.create_private_root(membership_tool)
        transaction.commit()

        with ZODBStorageInReadonlyMode():
            browser.login()
            membership_tool.createMemberarea()
            transaction.commit()

        member = membership_tool.getAuthenticatedMember()
        self.assertEqual(TEST_USER_ID, member.getId())

    @browsing
    def test_login_during_readonly(self, browser):
        """While the tests above test individual patches, this test fires all
        the login related events via loginUser() and makes sure that
        login as a whole works during readonly mode.
        """
        membership_tool = api.portal.get_tool('portal_membership')
        self.create_private_root(membership_tool)
        transaction.commit()

        with ZODBStorageInReadonlyMode():
            browser.login()
            membership_tool.loginUser()
            transaction.commit()

        member = membership_tool.getAuthenticatedMember()
        self.assertEqual(TEST_USER_ID, member.getId())

    @patch('ftw.casauth.plugin.validate_ticket')
    def test_caslogin_during_readonly(self, mock_validate_ticket):
        applyProfile(self.layer['portal'], 'opengever.setup:casauth')
        cas_plugin = self.portal.acl_users.cas_auth

        # Get any pending writes out of the way that would otherwise
        # trigger a ReadOnlyError during commit() below
        transaction.commit()

        mock_validate_ticket.return_value = TEST_USER_NAME
        creds = {
            'extractor': cas_plugin.getId(),
            'ticket': 'ST-001-abc',
            'service_url': 'http://127.0.0.1/'
        }

        with ZODBStorageInReadonlyMode():
            userid, login = cas_plugin.authenticateCredentials(creds)
            transaction.commit()

        self.assertEqual(TEST_USER_ID, userid)
        self.assertEqual(TEST_USER_NAME, login)
