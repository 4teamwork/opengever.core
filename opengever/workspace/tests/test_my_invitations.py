from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from mock import Mock
from mock import patch
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.base.security import elevated_privileges
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from opengever.workspace.interfaces import IWorkspaceSettings
from opengever.workspace.participation import load_signed_payload
from opengever.workspace.participation import serialize_and_sign_payload
from opengever.workspace.participation.browser.my_invitations import MyWorkspaceInvitations
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from zope.component import getUtility
import urlparse


FROZEN_NOW = datetime(2019, 12, 27, 12, 35)


class TestMyInvitationsView(IntegrationTestCase):

    features = ('workspace',)

    def setUp(self):
        super(TestMyInvitationsView, self).setUp()

        # Workspace installations only support one active orgunit
        ogds_service().fetch_org_unit("rk").enabled = False

        with self.login(self.workspace_admin):
            self.storage = getUtility(IInvitationStorage)

            self.workspace2 = create(Builder('workspace')
                                     .within(self.workspace_root)
                                     .titled(u'Second workspace'))

            with freeze(FROZEN_NOW):
                self.invitation_id = self.storage.add_invitation(
                    self.workspace, self.regular_user.getProperty('email'),
                    self.workspace_admin.getId(), 'WorkspaceGuest')
                self.storage.add_invitation(
                    self.workspace2, self.regular_user.getProperty('email'),
                    self.workspace_admin.getId(), 'WorkspaceGuest',
                    comment=u"another invitation")
                self.storage.add_invitation(
                    self.workspace2, self.workspace_guest.getProperty('email'),
                    self.workspace_admin.getId(), 'WorkspaceGuest')

                self.workspace_url = self.workspace.absolute_url()
                payload = serialize_and_sign_payload({'iid': self.invitation_id})
                self.accept_url = "{}/@@my-invitations/accept?invitation={}".format(
                    self.workspace_url, payload)
                self.decline_url = "{}/@@my-invitations/decline?invitation={}".format(
                    self.workspace_url, payload)

            RoleAssignmentManager(self.workspace_root).add_or_update_assignment(
                SharingRoleAssignment(self.regular_user.getId(),
                                      ['WorkspacesUser']))

    @browsing
    def test_my_invitations_accept_and_decline_are_public(self, browser):
        browser.allow_redirects = False
        browser.open(self.accept_url)
        browser.open(self.decline_url)

    @browsing
    def test_my_invitations_is_forbidden(self, browser):
        self.login(self.manager, browser=browser)
        with browser.expect_http_error():
            browser.open("{}/@@my-invitations".format(self.workspace_url))

    @browsing
    def test_accept_invitation_when_not_signed_in(self, browser):
        self.maxDiff = None
        with freeze(FROZEN_NOW):
            # redirect fails because portal is not set up
            with browser.expect_http_error():
                browser.open(self.accept_url)

            # check that we get redirected to login
            parsed_url = urlparse.urlparse(browser.url)
            self.assertEqual('/portal/login', parsed_url.path)


            # with redirect_url to accept the invitation and no_redirect in payload
            payload = serialize_and_sign_payload({'iid': self.invitation_id,
                                                      u'no_redirect': 1})
            accept_url = "{}/@@my-invitations/accept?invitation={}".format(
                self.workspace_url, payload)
            params = urlparse.parse_qs(parsed_url.query)
            self.assertDictEqual({'next': [accept_url]}, params)

    @browsing
    def test_accept_invitation_for_unknown_user(self, browser):
        # Getting the group DN does not work as we do not have an LDAP configured
        MyWorkspaceInvitations._get_orgunit_group_dn = Mock(return_value="group_dn")

        invitation = self.storage._write_invitations[self.invitation_id]
        invitation['recipient_email'] = 'unknown@example.com'
        # redirect fails because portal is not set up
        with browser.expect_http_error():
            browser.open(self.accept_url)

        # check that we get redirected to registration
        parsed_url = urlparse.urlparse(browser.url)
        self.assertEqual('/portal/registration', parsed_url.path)

        # with signed payload
        params = urlparse.parse_qs(parsed_url.query)

        payload = load_signed_payload(params["invitation"][0])
        self.assertEqual(["invitation"], params.keys())
        self.assertEqual("group_dn", payload["group"])
        self.assertEqual("unknown@example.com", payload['email'])

        self.login(self.workspace_admin, browser)
        callback = urlparse.urlparse(payload["callback"])
        self.assertEqual(
            "{}/@@my-invitations/accept".format(self.workspace.absolute_url_path()),
            callback.path)
        callback_payload = load_signed_payload(
            urlparse.parse_qs(callback.query)['invitation'][0])
        self.assertDictEqual(
            {u'new_user': 1, u'iid': self.invitation_id, u'no_redirect': 1},
            callback_payload)

    @browsing
    def test_accept_invitation_grants_local_roles(self, browser):
        self.login(self.regular_user, browser=browser)

        with elevated_privileges():
            assignments = RoleAssignmentManager(
                self.workspace).get_assignments_by_principal_id(self.regular_user.getId())
        self.assertEqual(0, len(assignments))

        browser.open(self.accept_url)

        with elevated_privileges():
            assignments = RoleAssignmentManager(
                self.workspace).get_assignments_by_principal_id(self.regular_user.getId())
        self.assertEqual(1, len(assignments))
        assignment = assignments[0]
        self.assertEqual(u'label_assignment_via_sharing',
                         assignment.cause_title())
        self.assertEqual(['WorkspaceGuest'], assignment.roles)
        self.assertEqual(self.regular_user.getId(), assignment.principal)

    @browsing
    def test_accept_invitation_grants_access_to_workspace(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_unauthorized():
            browser.open(self.workspace_url)

        browser.open(self.accept_url)

        browser.open(self.workspace_url)

    @browsing
    def test_accept_invitation_maps_invitations_with_same_email_to_current_user(self, browser):
        self.login(self.regular_user, browser=browser)
        for iid, invitation in self.storage._write_invitations.items():
            invitation['recipient'] = None
        self.assertEqual([None, None],
                         [invitation['recipient'] for invitation in
                          self.storage.iter_invitations_for_current_user()])

        browser.open(self.accept_url)
        self.assertEqual([self.regular_user.getId()],
                         [invitation['recipient'] for invitation in
                          self.storage.iter_invitations_for_current_user()])


    @browsing
    def test_invitation_can_only_be_accepted_once(self, browser):
        self.login(self.regular_user, browser=browser)
        invitations = tuple(self.storage.iter_invitations_for_current_user())
        self.assertEqual(2, len(invitations))

        browser.open(self.accept_url)

        invitations = tuple(self.storage.iter_invitations_for_current_user())
        self.assertEqual(1, len(invitations))
        with browser.expect_http_error(400):
            browser.open(self.accept_url)

    @browsing
    def test_cannot_accept_invalid_invitation(self, browser):
        self.login(self.regular_user, browser=browser)
        with freeze(FROZEN_NOW):
            payload = serialize_and_sign_payload({'iid': 'someinvalidiid'})
        accept_url = "{}/@@my-invitations/accept?invitation={}".format(
            self.workspace_url, payload)
        with browser.expect_http_error(400):
            browser.open(accept_url)

    @browsing
    def test_decline_invitation_invalidates_it(self, browser):
        self.login(self.regular_user, browser=browser)
        invitations = tuple(self.storage.iter_invitations_for_current_user())
        self.assertEqual(2, len(invitations))

        # declining redirects to the my-invitations view which will exist only
        # in the new frontend
        browser.allow_redirects = False
        browser.open(self.decline_url)
        browser.allow_redirects = True

        invitations = tuple(self.storage.iter_invitations_for_current_user())
        self.assertEqual(1, len(invitations))
        with browser.expect_http_error(400):
            browser.open(self.accept_url)

    @browsing
    def test_cannot_access_workspace_of_declined_invitation(self, browser):
        self.login(self.regular_user, browser=browser)

        # declining redirects to the my-invitations view which will exist only
        # in the new frontend
        browser.allow_redirects = False
        browser.open(self.decline_url)
        browser.allow_redirects = True

        with browser.expect_unauthorized():
            browser.open(self.workspace_url)

    @browsing
    def test_cannot_decline_invalid_invitation(self, browser):
        self.login(self.regular_user, browser=browser)

        with freeze(FROZEN_NOW):
            payload = serialize_and_sign_payload({'iid': 'someinvalidiid'})
        decline_url = "{}/@@my-invitations/decline?invitation={}".format(
            self.workspace_url, payload)
        with browser.expect_http_error(400):
            browser.open(decline_url)

    @browsing
    def test_my_invitation_link_personal_action(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.visit()
        self.assertTrue(browser.css('[href$="@@my-invitations"]'))

        self.deactivate_feature('workspace')
        browser.reload()
        self.assertFalse(browser.css('[href$="@@my-invitations"]'))

    def test_get_default_group_dn(self):
        with patch(
            'opengever.workspace.participation.browser.my_invitations.'
            'MyWorkspaceInvitations._get_orgunit_group_dn'
        ) as mocked_get_orgunit_group_dn:
            mocked_get_orgunit_group_dn.return_value = 'CN=Some Group'
            view = self.portal.unrestrictedTraverse('@@my-invitations')
            self.assertEqual(view.get_group_dn(), 'CN=Some Group')

    def test_get_group_dn_from_registry(self):
        api.portal.set_registry_record(
            'invitation_group_dn',
            interface=IWorkspaceSettings,
            value=u'CN=External Users',
        )
        view = self.portal.unrestrictedTraverse('@@my-invitations')
        self.assertEqual(view.get_group_dn(), 'CN=External Users')
