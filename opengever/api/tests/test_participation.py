from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.storage import IInvitationStorage
from plone.restapi.serializer.converters import json_compatible
from zExceptions import Unauthorized
from zope.component import getUtility
import json


def http_headers():
    return {'Accept': 'application/json',
            'Content-Type': 'application/json'}


def get_entry_by_token(entries, token):
    for entry in entries:
        if entry['token'] == token:
            return entry
    return None


class TestParticipationGet(IntegrationTestCase):

    @browsing
    def test_list_all_current_participants_and_invitations(self, browser):
        self.login(self.workspace_owner, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/beatrice.schrodinger',
                    u'@type': u'virtual.participations.user',
                    u'is_editable': True,
                    u'inviter_fullname': None,
                    u'participant_fullname': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
                    u'token': 'beatrice.schrodinger',
                    u'readable_role': u'Member',
                    u'role': u'WorkspaceMember',
                    u'participation_type': u'user',
                    u'readable_participation_type': u'User',
                },
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/fridolin.hugentobler',
                    u'@type': u'virtual.participations.user',
                    u'is_editable': True,
                    u'inviter_fullname': None,
                    u'participant_fullname': u'Hugentobler Fridolin (fridolin.hugentobler)',
                    u'token': 'fridolin.hugentobler',
                    u'readable_role': u'Admin',
                    u'role': u'WorkspaceAdmin',
                    u'participation_type': u'user',
                    u'readable_participation_type': u'User',
                },
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/gunther.frohlich',
                    u'@type': u'virtual.participations.user',
                    u'is_editable': False,
                    u'inviter_fullname': None,
                    u'participant_fullname': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)',
                    u'token': 'gunther.frohlich',
                    u'readable_role': u'Owner',
                    u'role': u'WorkspaceOwner',
                    u'participation_type': u'user',
                    u'readable_participation_type': u'User',
                },
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/hans.peter',
                    u'@type': u'virtual.participations.user',
                    u'is_editable': True,
                    u'inviter_fullname': None,
                    u'participant_fullname': u'Peter Hans (hans.peter)',
                    u'token': 'hans.peter',
                    u'readable_role': u'Guest',
                    u'role': u'WorkspaceGuest',
                    u'participation_type': u'user',
                    u'readable_participation_type': u'User',
                },
            ], response.get('items'))

    @browsing
    def test_owner_is_not_editable(self, browser):
        self.login(self.workspace_admin, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        items = response.get('items')

        self.assertFalse(
            get_entry_by_token(items, self.workspace_owner.id)['is_editable'],
            'The admin should not be able to manage himself')

    @browsing
    def test_current_logged_in_admin_cannot_edit_himself(self, browser):
        self.login(self.workspace_admin, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        items = response.get('items')

        self.assertFalse(
            get_entry_by_token(items, self.workspace_admin.id)['is_editable'],
            'The admin should not be able to manage himself')

        self.assertTrue(
            get_entry_by_token(items, 'hans.peter')['is_editable'],
            'The admin should be able to manage hans.peter')

    @browsing
    def test_an_admin_can_edit_other_members(self, browser):
        self.login(self.workspace_admin, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        items = response.get('items')

        self.assertTrue(
            get_entry_by_token(items, self.workspace_guest.id)['is_editable'],
            'The admin should be able to manage {}'.format(self.workspace_guest.id))

    @browsing
    def test_user_without_sharing_permission_cannot_manage(self, browser):
        self.login(self.workspace_member, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertFalse(
            any([item.get('is_editable') for item in response.get('items')]),
            'No entry should be editable because the user has no permission')

    @browsing
    def test_get_single_invitation(self, browser):
        self.login(self.workspace_owner, browser)

        iid = getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        response = browser.open(
            self.workspace.absolute_url() + '/@invitations/{}'.format(iid),
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/workspaces/workspace-1/@invitations/{}'.format(iid),
                u'@type': u'virtual.participations.invitation',
                u'is_editable': True,
                u'inviter_fullname': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)',
                u'participant_fullname': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                u'token': iid,
                u'readable_role': u'Guest',
                u'role': u'WorkspaceGuest',
                u'participation_type': u'invitation',
                u'readable_participation_type': u'Invitation',
            }, response)

    @browsing
    def test_get_single_participant(self, browser):
        self.login(self.workspace_owner, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations/{}'.format(self.workspace_guest.id),
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/hans.peter',
                u'@type': u'virtual.participations.user',
                u'is_editable': True,
                u'inviter_fullname': None,
                u'participant_fullname': u'Peter Hans (hans.peter)',
                u'token': 'hans.peter',
                u'readable_role': u'Guest',
                u'role': u'WorkspaceGuest',
                u'participation_type': u'user',
                u'readable_participation_type': u'User',
            }, response)


class TestParticipationDelete(IntegrationTestCase):

    @browsing
    def test_delete_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)
        storage = getUtility(IInvitationStorage)
        iid = storage.add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_admin.getId(),
            'WorkspaceGuest')

        browser.open(
            self.workspace.absolute_url() + '/@invitations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_token(browser.json.get('items'), iid),
            'Expect an invitation.')

        browser.open(
            self.workspace.absolute_url() + '/@invitations/{}'.format(iid),
            method='DELETE',
            headers=http_headers(),
        )

        self.assertEqual(204, browser.status_code)

        browser.open(
            self.workspace.absolute_url() + '/@invitations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_token(browser.json.get('items'), iid),
            'Expect no invitation anymore.')

    @browsing
    def test_delete_local_role(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_token(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have local roles for the user')

        browser.open(
            self.workspace.absolute_url() + '/@participations/{}'.format(self.workspace_guest.id),
            method='DELETE',
            headers=http_headers(),
        )

        self.assertEqual(204, browser.status_code)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_token(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user')

    @browsing
    def test_current_user_cannot_remove_its_local_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + '/@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers(),
            ).json

    @browsing
    def test_guest_cannot_use_the_endpoint(self, browser):
        self.login(self.workspace_guest, browser=browser)

        with browser.expect_http_error(401):
            browser.open(
                self.workspace.absolute_url() + '/@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers(),
            ).json

    @browsing
    def test_member_cannot_use_the_endpoint(self, browser):
        self.login(self.workspace_member, browser=browser)

        with browser.expect_http_error(401):
            browser.open(
                self.workspace.absolute_url() + '/@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers(),
            ).json


class TestParticipationPatch(IntegrationTestCase):

    @browsing
    def test_modify_a_users_loca_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_token(browser.json.get('items'), self.workspace_guest.id)
        self.assertEquals('WorkspaceGuest', entry.get('role'))

        data = json.dumps(json_compatible({
            'role': {'token': 'WorkspaceMember'}
        }))
        browser.open(
            entry['@id'],
            method='PATCH',
            data=data,
            headers=http_headers(),
            )

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_token(browser.json.get('items'), self.workspace_guest.id)
        self.assertEquals('WorkspaceMember', entry.get('role'))

    @browsing
    def test_cannot_modify_inexisting_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with browser.expect_http_error(400):
            data = json.dumps(json_compatible({
                'role': {'token': 'WorkspaceMember'}
            }))
            browser.open(
                self.workspace.absolute_url() + '/@participations/{}'.format(self.regular_user.id),
                method='PATCH',
                data=data,
                headers=http_headers(),
                )

    @browsing
    def test_can_only_modify_workspace_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_token(browser.json.get('items'), self.workspace_guest.id)

        with browser.expect_http_error(401):
            data = json.dumps(json_compatible({
                'role': {'token': 'Contributor'}
            }))

            browser.open(
                entry['@id'],
                method='PATCH',
                data=data,
                headers=http_headers(),
                )

    @browsing
    def test_modify_role_of_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)

        storage = getUtility(IInvitationStorage)
        iid = storage.add_invitation(
            self.workspace, self.regular_user.getProperty('email'),
            self.workspace_admin.getId(), 'WorkspaceGuest')

        data = json.dumps(json_compatible({
            'role': {'token': 'WorkspaceAdmin'}
        }))

        browser.open(
            self.workspace.absolute_url() + '/@invitations/{}'.format(iid),
            method='PATCH',
            data=data,
            headers=http_headers(),
            )

        browser.open(
            self.workspace.absolute_url() + '/@invitations',
            method='GET',
            headers=http_headers(),
        )

        self.assertEquals(
            'WorkspaceAdmin',
            get_entry_by_token(browser.json.get('items'), iid).get('role'))

    @browsing
    def test_do_not_allow_modifying_the_WorkspaceOwnerRole(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_token(browser.json.get('items'), self.workspace_owner.id)

        with browser.expect_http_error(400):
            data = json.dumps(json_compatible({
                'role': {'token': 'WorkspaceAdmin'}
            }))

            browser.open(
                entry['@id'],
                method='PATCH',
                data=data,
                headers=http_headers(),
                )

    @browsing
    def test_do_not_allow_modifying_the_current_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_token(browser.json.get('items'), self.workspace_admin.id)

        with browser.expect_http_error(401):
            data = json.dumps(json_compatible({
                'role': {'token': 'WorkspaceMember'}
            }))

            browser.open(
                entry['@id'],
                method='PATCH',
                data=data,
                headers=http_headers(),
                )


class TestMyInvitationsGet(IntegrationTestCase):

    @browsing
    def test_list_all_my_invitations(self, browser):
        self.login(self.workspace_owner, browser)

        with freeze(datetime(2018, 4, 30, 10, 30)):
            iid = getUtility(IInvitationStorage).add_invitation(
                self.workspace,
                self.regular_user.getProperty('email'),
                self.workspace_owner.getId(),
                'WorkspaceGuest')

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.reader_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.regular_user, browser)

        response = browser.open(
            self.portal.absolute_url() + '/@my-workspace-invitations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [
                {
                    u'@id': u'http://nohost/plone/@workspace-invitations/{}'.format(iid),
                    u'@type': u'virtual.participations.invitation',
                    u'accept': u'http://nohost/plone/@workspace-invitations/{}/accept'.format(iid),
                    u'created': u'2018-04-30T10:30:00+00:00',
                    u'decline': u'http://nohost/plone/@workspace-invitations/{}/decline'.format(iid),
                    u'inviter_fullname': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)',
                    u'title': u'A Workspace'
                }
            ], response.get('items'))


class TestInvitationsPOST(IntegrationTestCase):

    def get_my_invitations(self, browser):
        return browser.open(
            self.portal.absolute_url() + '/@my-workspace-invitations',
            method='GET',
            headers=http_headers(),
        ).json

    @browsing
    def test_accept_invitation(self, browser):
        self.login(self.workspace_owner, browser)

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.regular_user, browser)

        with self.assertRaises(Unauthorized):
            browser.visit(self.workspace)

        my_invitations = self.get_my_invitations(browser)

        # Accept first invitation
        json_workspace = browser.open(
            my_invitations.get('items')[0].get('accept'),
            method='POST',
            headers=http_headers()).json

        my_invitations = self.get_my_invitations(browser)
        self.assertEqual([], my_invitations.get('items'))

        self.assertEqual(200, browser.visit(json_workspace['@id']).status_code)

    @browsing
    def test_decline_invitation(self, browser):
        self.login(self.workspace_owner, browser)

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.regular_user, browser)

        with self.assertRaises(Unauthorized):
            browser.visit(self.workspace)

        my_invitations = self.get_my_invitations(browser)

        # Decline first invitation
        browser.open(
            my_invitations.get('items')[0].get('decline'),
            method='POST',
            headers=http_headers()).json

        my_invitations = self.get_my_invitations(browser)
        self.assertEqual([], my_invitations.get('items'))

        with self.assertRaises(Unauthorized):
            browser.visit(self.workspace)

    @browsing
    def test_disallow_accept_invitation_of_other_user(self, browser):
        self.login(self.workspace_owner, browser)

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.regular_user, browser)

        my_invitations = self.get_my_invitations(browser)
        accept_link = my_invitations.get('items')[0].get('accept')

        self.login(self.workspace_owner, browser)

        # Accept invitation of regular-user
        with browser.expect_http_error(400):
            browser.open(
                accept_link,
                method='POST',
                headers=http_headers()).json

        self.login(self.regular_user, browser)
        my_invitations = self.get_my_invitations(browser)
        self.assertEqual(1, len(my_invitations.get('items')))

    @browsing
    def test_disallow_decline_invitation_of_other_user(self, browser):
        self.login(self.workspace_owner, browser)

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.regular_user, browser)

        my_invitations = self.get_my_invitations(browser)
        accept_link = my_invitations.get('items')[0].get('decline')

        self.login(self.workspace_owner, browser)

        # Decline invitation of regular-user
        with browser.expect_http_error(400):
            browser.open(
                accept_link,
                method='POST',
                headers=http_headers()).json

        self.login(self.regular_user, browser)
        my_invitations = self.get_my_invitations(browser)
        self.assertEqual(1, len(my_invitations.get('items')))

    @browsing
    def test_raise_404_for_unknown_action(self, browser):
        self.login(self.workspace_owner, browser)

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.regular_user, browser)

        my_invitations = self.get_my_invitations(browser)
        accept_link = my_invitations.get('items')[0].get('decline')

        self.login(self.workspace_owner, browser)

        # Decline invitation of regular-user
        with browser.expect_http_error(404):
            browser.open(
                accept_link + 'unknown',
                method='POST',
                headers=http_headers()).json
