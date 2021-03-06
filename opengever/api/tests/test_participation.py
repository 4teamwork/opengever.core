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


def get_entry_by_id(entries, token):
    for entry in entries:
        if entry['participant']['id'] == token:
            return entry
    return None


def block_role_inheritance(obj, browser, copy_roles=False):
    browser.open(
        obj.absolute_url() + '/@role-inheritance',
        data=json.dumps({'blocked': True, 'copy_roles': copy_roles}),
        method='POST',
        headers=http_headers())


def remove_participation(obj, browser, token):
    browser.open(
        obj.absolute_url() + '/@participations/{}'.format(token),
        method='DELETE',
        headers=http_headers(),
    )


def add_participation(obj, browser, token, role):
    browser.open(
        obj.absolute_url() + '/@participations/{}'.format(token),
        method='POST',
        headers=http_headers(),
        data=json.dumps({'participant': token, 'role': role})
    )


class TestParticipationGet(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_list_all_current_participants_and_invitations(self, browser):
        self.login(self.workspace_owner, browser)
        add_participation(self.workspace, browser, 'projekt_a', 'WorkspaceMember')

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [{u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/beatrice.schrodinger',
              u'@type': u'virtual.participations.user',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/beatrice.schrodinger',
                  u'identifier': u'beatrice.schrodinger'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/beatrice.schrodinger',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'beatrice.schrodinger@gever.local',
                               u'id': u'beatrice.schrodinger',
                               u'is_local': None,
                               u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)'},
              u'role': {u'title': u'Member', u'token': u'WorkspaceMember'}},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/fridolin.hugentobler',
              u'@type': u'virtual.participations.user',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/fridolin.hugentobler',
                  u'identifier': u'fridolin.hugentobler'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/fridolin.hugentobler',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'fridolin.hugentobler@gever.local',
                               u'id': u'fridolin.hugentobler',
                               u'is_local': None,
                               u'title': u'Hugentobler Fridolin (fridolin.hugentobler)'},
              u'role': {u'title': u'Admin', u'token': u'WorkspaceAdmin'}},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/gunther.frohlich',
              u'@type': u'virtual.participations.user',
              u'is_editable': False,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/gunther.frohlich',
                  u'identifier': u'gunther.frohlich'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/gunther.frohlich',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'gunther.frohlich@gever.local',
                               u'id': u'gunther.frohlich',
                               u'is_local': None,
                               u'title': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)'},
              u'role': {u'title': u'Admin', u'token': u'WorkspaceAdmin'}},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/hans.peter',
              u'@type': u'virtual.participations.user',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/hans.peter',
                  u'identifier': u'hans.peter'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/hans.peter',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'hans.peter@gever.local',
                               u'id': u'hans.peter',
                               u'is_local': None,
                               u'title': u'Peter Hans (hans.peter)'},
              u'role': {u'title': u'Guest', u'token': u'WorkspaceGuest'}},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/projekt_a',
              u'@type': u'virtual.participations.group',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/projekt_a',
                  u'identifier': u'projekt_a'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
                               u'@type': u'virtual.ogds.group',
                               u'active': True,
                               u'email': None,
                               u'id': u'projekt_a',
                               u'is_local': False,
                               u'title': u'Projekt A'},
              u'role': {u'title': u'Member', u'token': u'WorkspaceMember'}}],
            response.get('items'))

    @browsing
    def test_list_all_current_participants_in_folder_lists_participants_of_the_workspace(self, browser):
        self.login(self.workspace_owner, browser)

        response = browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [
                u'http://nohost/plone/workspaces/workspace-1/@participations/beatrice.schrodinger',
                u'http://nohost/plone/workspaces/workspace-1/@participations/fridolin.hugentobler',
                u'http://nohost/plone/workspaces/workspace-1/@participations/gunther.frohlich',
                u'http://nohost/plone/workspaces/workspace-1/@participations/hans.peter',
            ], [item.get('@id') for item in response.get('items')])

    @browsing
    def test_list_all_folder_participants_with_blocked_role_inheritance_in_folder(self, browser):
        self.login(self.workspace_owner, browser)

        block_role_inheritance(self.workspace_folder, browser, copy_roles=True)

        response = browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/beatrice.schrodinger',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/fridolin.hugentobler',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/gunther.frohlich',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/hans.peter',
            ], [item.get('@id') for item in response.get('items')])

    @browsing
    def test_admin_cannot_edit_himself(self, browser):
        self.login(self.workspace_owner, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        items = response.get('items')

        self.assertFalse(
            get_entry_by_id(items, self.workspace_owner.id)['is_editable'],
            'The admin should not be able to manage himself')

    @browsing
    def test_manages_invalid_participant(self, browser):
        self.login(self.manager, browser)

        self.workspace.__ac_local_roles__ = {'invalid_participant': ['WorkspaceAdmin']}

        response = browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [{u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/invalid_participant',
              u'@type': u'virtual.participations.null',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/invalid_participant',
                  u'identifier': u'invalid_participant'},
              u'participant': {u'@id': None,
                               u'@type': None,
                               u'active': None,
                               u'email': None,
                               u'id': u'invalid_participant',
                               u'is_local': None,
                               u'title': u'invalid_participant'},
              u'role': {u'title': u'Admin', u'token': u'WorkspaceAdmin'}}],
            response.get('items'))

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
            get_entry_by_id(items, self.workspace_admin.id)['is_editable'],
            'The admin should not be able to manage himself')

        self.assertTrue(
            get_entry_by_id(items, 'hans.peter')['is_editable'],
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
            get_entry_by_id(items, self.workspace_guest.id)['is_editable'],
            'The admin should be able to manage {}'.format(self.workspace_guest.id))

    @browsing
    def test_an_admin_can_only_edit_other_members_if_role_inheritance_is_blocked(self, browser):
        self.login(self.workspace_admin, browser)

        response = browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        ).json

        items = response.get('items')

        self.assertFalse(
            get_entry_by_id(items, self.workspace_guest.id)['is_editable'],
            'The admin should not be able to manage {}'.format(self.workspace_guest.id))

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
    def test_get_single_user_participant(self, browser):
        self.login(self.workspace_owner, browser)

        response = browser.open(
            self.workspace.absolute_url() + '/@participations/{}'.format(self.workspace_guest.id),
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/hans.peter',
             u'@type': u'virtual.participations.user',
             u'is_editable': True,
             u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/hans.peter',
                  u'identifier': u'hans.peter'},
             u'participant': {u'@id': u'http://nohost/plone/@ogds-users/hans.peter',
                              u'@type': u'virtual.ogds.user',
                              u'active': True,
                              u'email': u'hans.peter@gever.local',
                              u'id': u'hans.peter',
                              u'is_local': None,
                              u'title': u'Peter Hans (hans.peter)'},
             u'role': {u'title': u'Guest', u'token': u'WorkspaceGuest'}},
            response)

    @browsing
    def test_get_single_group_participant(self, browser):
        self.login(self.workspace_owner, browser)

        add_participation(self.workspace, browser, 'projekt_a', 'WorkspaceMember')

        response = browser.open(
            self.workspace.absolute_url() + '/@participations/projekt_a',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/projekt_a',
             u'@type': u'virtual.participations.group',
             u'is_editable': True,
             u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/projekt_a',
                  u'identifier': u'projekt_a'},
             u'participant': {u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
                              u'@type': u'virtual.ogds.group',
                              u'active': True,
                              u'email': None,
                              u'id': u'projekt_a',
                              u'is_local': False,
                              u'title': u'Projekt A'},
             u'role': {u'title': u'Member', u'token': u'WorkspaceMember'}},
            response)


class TestParticipationDelete(IntegrationTestCase):

    @browsing
    def test_delete_user_local_role(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
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
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user')

    @browsing
    def test_delete_group_local_role(self, browser):
        self.login(self.workspace_admin, browser=browser)

        add_participation(self.workspace, browser, 'projekt_a', 'WorkspaceGuest')

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), 'projekt_a'),
            'Expect to have local roles for the group')

        browser.open(
            self.workspace.absolute_url() + '/@participations/projekt_a',
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
            get_entry_by_id(browser.json.get('items'), 'projekt_a'),
            'Expect to have no local roles anymore for the group')

    @browsing
    def test_delete_local_role_from_folder(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser, copy_roles=True)

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have local roles for the user')

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations/{}'.format(self.workspace_guest.id),
            method='DELETE',
            headers=http_headers(),
        )

        self.assertEqual(204, browser.status_code)

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user')

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to still have local roles for the user on the workspace')

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

    @browsing
    def test_remove_local_roles_from_self_managed_folders_if_removed_in_upper_context(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations/{}'.format(self.workspace_guest.id),
            method='DELETE',
            headers=http_headers(),
        )

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user in the workspace')

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user in the folder')


class TestParticipationPatch(IntegrationTestCase):

    @browsing
    def test_modify_a_users_local_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEquals(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

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

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEquals(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'))

    @browsing
    def test_modify_a_groups_local_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        add_participation(self.workspace, browser, 'projekt_a', 'WorkspaceGuest')

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), 'projekt_a')
        self.assertEquals(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

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

        entry = get_entry_by_id(browser.json.get('items'), 'projekt_a')
        self.assertEquals(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'))

    @browsing
    def test_modify_a_users_local_role_on_folder(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser, copy_roles=True)

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEquals(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

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
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEquals(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'),
            'Expect to have the WorkspaceMember role')

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEquals(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'),
            'Expect to still have the WorkspaceGuest role on the workspace')

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

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)

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
    def test_do_not_allow_modifying_the_current_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_admin.id)

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


class TestParticipationPostWorkspace(IntegrationTestCase):

    @browsing
    def test_let_a_user_participate(self, browser):
        self.login(self.workspace_admin, browser=browser)

        remove_participation(self.workspace, browser, self.workspace_member.id)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertIsNone(entry)

        data = {
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'WorkspaceGuest'},
        }

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='POST',
            data=json.dumps(data),
            headers=http_headers(),
            )

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertEquals(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

    @browsing
    def test_let_a_group_participate(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), 'projekt_a')
        self.assertIsNone(entry)

        data = {
            "participant": {"token": 'projekt_a'},
            "role": {"token": 'WorkspaceGuest'},
        }

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='POST',
            data=json.dumps(data),
            headers=http_headers(),
            )

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), 'projekt_a')
        self.assertEquals(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

    @browsing
    def test_inexistant_user_cannot_participate(self, browser):
        self.login(self.workspace_admin, browser=browser)

        data = {
            "participant": {"token": 'not-existing-user'},
            "role": {"token": 'WorkspaceGuest'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

    @browsing
    def test_can_only_assign_predefined_workspace_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        remove_participation(self.workspace, browser, self.workspace_member.id)

        data = {
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'Manager'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

    @browsing
    def test_only_one_participation_per_user_is_allowed(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertIsNotNone(entry)

        data = {
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'WorkspaceGuest'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )


class TestParticipationPostWorkspaceFolder(IntegrationTestCase):

    @browsing
    def test_let_a_user_participate_to_a_folder(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser)
        remove_participation(self.workspace_folder, browser, self.workspace_member.id)

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertIsNone(entry)

        data = {
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'WorkspaceGuest'},
        }

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='POST',
            data=json.dumps(data),
            headers=http_headers(),
            )

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertEquals(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

    @browsing
    def test_do_not_allow_to_participate_a_user_to_a_folder_if_role_inheritance_is_not_blocked(self, browser):
        self.login(self.workspace_admin, browser=browser)

        data = {
            "participant": {"token": self.regular_user.id},
            "role": {"token": 'WorkspaceGuest'},
        }

        with browser.expect_http_error(403):
            browser.open(
                self.workspace_folder.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

    @browsing
    def test_cannot_participate_an_inexisting_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser)

        data = {
            "participant": {"token": 'not-existing-user'},
            "role": {"token": 'WorkspaceGuest'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace_folder.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

    @browsing
    def test_can_only_assign_predefined_workspace_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser)
        remove_participation(self.workspace_folder, browser, self.workspace_member.id)

        data = {
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'Manager'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace_folder.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

        self.assertEqual('BadRequest', browser.json.get('type'))
        self.assertIn('Role is not availalbe. Available roles are:',
                      browser.json.get('message'))

    @browsing
    def test_do_not_allow_readding_an_already_existing_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser, copy_roles=True)

        browser.open(
            self.workspace_folder.absolute_url() + '/@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertIsNotNone(entry)

        data = {
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'WorkspaceGuest'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace_folder.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

        self.assertEqual({"message": "The participant already exists",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_only_users_from_the_upper_context_are_allowed_to_participate_to_a_folder(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser)
        remove_participation(self.workspace, browser, self.workspace_member.id)
        remove_participation(self.workspace_folder, browser, self.workspace_member.id)

        data = {
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'WorkspaceGuest'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace_folder.absolute_url() + '/@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

        self.assertEqual({"message": "The participant is not allowed",
                          "type": "BadRequest"}, browser.json)


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
                    u'title': u'A Workspace',
                    u'comment': u''
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
