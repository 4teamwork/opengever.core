from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.storage import IInvitationStorage
from plone.restapi.serializer.converters import json_compatible
from zExceptions import Forbidden
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
        obj,
        view='@role-inheritance',
        data=json.dumps({'blocked': True, 'copy_roles': copy_roles}),
        method='POST',
        headers=http_headers())


def remove_participation(obj, browser, token):
    browser.open(
        obj,
        view='@participations/{}'.format(token),
        method='DELETE',
        headers=http_headers(),
    )


def add_participation(obj, browser, token, role):
    browser.open(
        obj,
        view='/@participations/{}'.format(token),
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
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [{u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_member',
              u'@type': u'virtual.participations.user',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/workspace_member',
                  u'identifier': u'workspace_member'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/beatrice.schrodinger',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'beatrice.schrodinger@gever.local',
                               u'id': u'workspace_member',
                               u'is_local': None,
                               u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)'},
              u'role': {u'title': u'Member', u'token': u'WorkspaceMember'}},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_admin',
              u'@type': u'virtual.participations.user',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/workspace_admin',
                  u'identifier': u'workspace_admin'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/fridolin.hugentobler',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'fridolin.hugentobler@gever.local',
                               u'id': u'workspace_admin',
                               u'is_local': None,
                               u'title': u'Hugentobler Fridolin (fridolin.hugentobler)'},
              u'role': {u'title': u'Admin', u'token': u'WorkspaceAdmin'}},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_owner',
              u'@type': u'virtual.participations.user',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/workspace_owner',
                  u'identifier': u'workspace_owner'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/gunther.frohlich',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'gunther.frohlich@gever.local',
                               u'id': u'workspace_owner',
                               u'is_local': None,
                               u'title': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)'},
              u'role': {u'title': u'Admin', u'token': u'WorkspaceAdmin'}},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_guest',
              u'@type': u'virtual.participations.user',
              u'is_editable': True,
              u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/workspace_guest',
                  u'identifier': u'workspace_guest'},
              u'participant': {u'@id': u'http://nohost/plone/@ogds-users/hans.peter',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'email': u'hans.peter@gever.local',
                               u'id': u'workspace_guest',
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
    def test_raises_forbidden_for_guests_if_members_are_hidden(self, browser):
        browser.exception_bubbling = True

        self.login(self.workspace_admin)
        self.workspace.hide_members_for_guests = True

        self.login(self.workspace_guest, browser)
        with self.assertRaises(Forbidden):
            browser.open(self.workspace, view='@participations',
                         method='GET', headers=self.api_headers)

    @browsing
    def test_list_all_current_participants_in_folder_lists_participants_of_the_workspace(self, browser):
        self.login(self.workspace_owner, browser)

        response = browser.open(
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [
                u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_member',
                u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_admin',
                u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_owner',
                u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_guest',
            ], [item.get('@id') for item in response.get('items')])

    @browsing
    def test_list_all_folder_participants_with_blocked_role_inheritance_in_folder(self, browser):
        self.login(self.workspace_owner, browser)

        block_role_inheritance(self.workspace_folder, browser, copy_roles=True)

        response = browser.open(
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertItemsEqual(
            [
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/workspace_member',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/workspace_admin',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/workspace_owner',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/@participations/workspace_guest',
            ], [item.get('@id') for item in response.get('items')])

    @browsing
    def test_admin_can_edit_himself(self, browser):
        self.login(self.workspace_admin, browser)

        response = browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        ).json

        items = response.get('items')

        self.assertTrue(
            get_entry_by_id(items, self.workspace_admin.id)['is_editable'],
            'The admin should be able to manage himself')

    @browsing
    def test_manages_invalid_participant(self, browser):
        self.login(self.manager, browser)

        self.workspace.__ac_local_roles__ = {'invalid_participant': ['WorkspaceAdmin']}

        response = browser.open(
            self.workspace,
            view='@participations',
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
                               u'title': u'Unknown ID (invalid_participant)'},
              u'role': {u'title': u'Admin', u'token': u'WorkspaceAdmin'}}],
            response.get('items'))


    @browsing
    def test_an_admin_can_edit_other_members(self, browser):
        self.login(self.workspace_admin, browser)

        response = browser.open(
            self.workspace,
            view='@participations',
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
            self.workspace_folder,
            view='@participations',
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
            self.workspace,
            view='@participations',
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
            self.workspace,
            view='@participations/{}'.format(self.workspace_guest.id),
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1/@participations/workspace_guest',
             u'@type': u'virtual.participations.user',
             u'is_editable': True,
             u'participant_actor': {
                  u'@id': u'http://nohost/plone/@actors/workspace_guest',
                  u'identifier': u'hans.peter'},
             u'participant': {u'@id': u'http://nohost/plone/@ogds-users/hans.peter',
                              u'@type': u'virtual.ogds.user',
                              u'active': True,
                              u'email': u'hans.peter@gever.local',
                              u'id': u'workspace_guest',
                              u'is_local': None,
                              u'title': u'Peter Hans (hans.peter)'},
             u'role': {u'title': u'Guest', u'token': u'WorkspaceGuest'}},
            response)

    @browsing
    def test_get_single_group_participant(self, browser):
        self.login(self.workspace_owner, browser)

        add_participation(self.workspace, browser, 'projekt_a', 'WorkspaceMember')

        response = browser.open(
            self.workspace,
            view='@participations/projekt_a',
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
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have local roles for the user')

        browser.open(
            self.workspace,
            view='@participations/{}'.format(self.workspace_guest.id),
            method='DELETE',
            headers=http_headers(),
        )

        self.assertEqual(204, browser.status_code)

        browser.open(
            self.workspace,
            view='@participations',
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
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), 'projekt_a'),
            'Expect to have local roles for the group')

        browser.open(
            self.workspace,
            view='@participations/projekt_a',
            method='DELETE',
            headers=http_headers(),
        )

        self.assertEqual(204, browser.status_code)

        browser.open(
            self.workspace,
            view='@participations',
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
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have local roles for the user')

        browser.open(
            self.workspace_folder,
            view='@participations/{}'.format(self.workspace_guest.id),
            method='DELETE',
            headers=http_headers(),
        )

        self.assertEqual(204, browser.status_code)

        browser.open(
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user')

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNotNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to still have local roles for the user on the workspace')

    @browsing
    def test_workspace_member_cannot_remove_its_local_roles(self, browser):
        self.login(self.workspace_member, browser=browser)

        with browser.expect_http_error(401):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_member.id),
                method='DELETE',
                headers=http_headers(),
            )

    @browsing
    def test_workspace_admin_can_remove_its_local_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace,
            view='@participations/{}'.format(self.workspace_admin.id),
            method='DELETE',
            headers=http_headers(),
        )

        with browser.expect_http_error(401):
            browser.open(
                self.workspace,
                view='@participations',
                method='GET',
                headers=http_headers(),
            )

    @browsing
    def test_cannot_delete_the_last_workspace_admin_role_assignment(self, browser):
        self.login(self.administrator, browser=browser)

        # we have two admins, deleting the first one should work
        browser.open(
            self.workspace,
            view='@participations/{}'.format(self.workspace_owner.id),
            method='DELETE',
            headers=http_headers()
        )
        with browser.expect_http_error(400):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers()
            )

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'At least one principal must remain admin.',
                         browser.json[u'translated_message'])

    @browsing
    def test_cannot_delete_if_user_is_participant_of_a_folder_on_which_one_does_not_have_admin_rights(self, browser):
        with self.login(self.workspace_admin, browser):
            block_role_inheritance(self.workspace_folder, browser, copy_roles=False)
            add_participation(self.workspace_folder, browser, self.workspace_member.id,
                              'WorkspaceGuest')
            add_participation(self.workspace_folder, browser, self.workspace_owner.id,
                              'WorkspaceMember')

        self.login(self.workspace_owner, browser=browser)

        with browser.expect_http_error(400):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_member.id),
                method='DELETE',
                headers=http_headers()
            )

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'The participant cannot be deleted because he has access to a subfolder'
                         u' on which you do not have admin rights.',
                         browser.json[u'translated_message'])

    @browsing
    def test_cannot_delete_if_user_is_participant_of_a_folder_on_which_one_does_not_have_view_permission(self, browser):
        with self.login(self.workspace_admin, browser):
            block_role_inheritance(self.workspace_folder, browser, copy_roles=False)
            add_participation(self.workspace_folder, browser, self.workspace_member.id,
                              'WorkspaceGuest')

        self.login(self.workspace_owner, browser=browser)

        with browser.expect_http_error(400):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_member.id),
                method='DELETE',
                headers=http_headers()
            )

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'The participant cannot be deleted because he has access to a subfolder'
                         u' on which you do not have admin rights.',
                         browser.json[u'translated_message'])

    @browsing
    def test_cannot_delete_if_user_is_only_workspace_admin_of_a_folder(self, browser):
        with self.login(self.workspace_admin, browser):
            block_role_inheritance(self.workspace_folder, browser, copy_roles=False)

        self.login(self.administrator, browser=browser)

        with browser.expect_http_error(400):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers()
            )

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'The participant cannot be deleted because he is the only administrator '
                         u'in a subfolder. At least one participant must remain an administrator.',
                         browser.json[u'translated_message'])

    @browsing
    def test_cannot_delete_the_last_folder_admin_role_assignment(self, browser):
        self.login(self.workspace_admin, browser=browser)
        block_role_inheritance(self.workspace_folder, browser, copy_roles=False)

        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(
                self.workspace_folder,
                view='@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers()
            )

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'At least one principal must remain admin.',
                         browser.json[u'translated_message'])

    @browsing
    def test_guest_cannot_use_the_endpoint(self, browser):
        self.login(self.workspace_guest, browser=browser)

        with browser.expect_http_error(401):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers(),
            ).json

    @browsing
    def test_member_cannot_use_the_endpoint(self, browser):
        self.login(self.workspace_member, browser=browser)

        with browser.expect_http_error(401):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_admin.id),
                method='DELETE',
                headers=http_headers(),
            ).json

    @browsing
    def test_remove_local_roles_from_self_managed_folders_if_removed_in_upper_context(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser)

        browser.open(
            self.workspace,
            view='@participations/{}'.format(self.workspace_guest.id),
            method='DELETE',
            headers=http_headers(),
        )

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user in the workspace')

        browser.open(
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        self.assertIsNone(
            get_entry_by_id(browser.json.get('items'), self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user in the folder')

    @browsing
    def test_delete_inactive_user_local_role(self, browser):
        self.login(self.workspace_admin, browser=browser)

        assignment_manager = RoleAssignmentManager(self.workspace)

        # add local_roles for inactive user
        assignment_manager.add_or_update(
            'inactive-user', ['WorkspaceGuest'], ASSIGNMENT_VIA_SHARING)

        browser.open(self.workspace, view='@participations',
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            get_entry_by_id(browser.json['items'], 'inactive-user').get('role'))

        browser.open(self.workspace, view='@participations/inactive-user',
                     method='DELETE', headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertEqual(
            [],
            assignment_manager.get_assignments_by_principal_id('inactive-user'))


class TestParticipationPatch(IntegrationTestCase):

    @browsing
    def test_modify_a_users_local_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEqual(
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
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEqual(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'))

    @browsing
    def test_modify_a_groups_local_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        add_participation(self.workspace, browser, 'projekt_a', 'WorkspaceGuest')

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), 'projekt_a')
        self.assertEqual(
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
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), 'projekt_a')
        self.assertEqual(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'))

    @browsing
    def test_cannot_modify_the_last_workspace_admin_role_assignment(self, browser):
        self.login(self.administrator, browser=browser)

        data = json.dumps(json_compatible({
            'role': {'token': 'WorkspaceMember'}
        }))
        # we have two admins, modifying the first one should work
        browser.open(
            self.workspace,
            view='@participations/{}'.format(self.workspace_owner.id),
            method='PATCH',
            data=data,
            headers=http_headers()
        )
        with browser.expect_http_error(400):
            browser.open(
                self.workspace,
                view='@participations/{}'.format(self.workspace_admin.id),
                method='PATCH',
                data=data,
                headers=http_headers()
            )

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'At least one principal must remain admin.',
                         browser.json[u'translated_message'])

    @browsing
    def test_cannot_modify_the_last_folder_admin_role_assignment(self, browser):
        self.login(self.workspace_admin, browser=browser)
        block_role_inheritance(self.workspace_folder, browser, copy_roles=False)

        self.login(self.administrator, browser=browser)

        data = json.dumps(json_compatible({
            'role': {'token': 'WorkspaceMember'}
        }))
        with browser.expect_http_error(400):
            browser.open(
                self.workspace_folder,
                view='@participations/{}'.format(self.workspace_admin.id),
                method='PATCH',
                data=data,
                headers=http_headers()
            )

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'At least one principal must remain admin.',
                         browser.json[u'translated_message'])

    @browsing
    def test_modify_a_users_local_role_on_folder(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser, copy_roles=True)

        browser.open(
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEqual(
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
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEqual(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'),
            'Expect to have the WorkspaceMember role')

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_guest.id)
        self.assertEqual(
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
                self.workspace,
                view='@participations/{}'.format(self.regular_user.id),
                method='PATCH',
                data=data,
                headers=http_headers(),
                )

    @browsing
    def test_can_only_modify_workspace_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace,
            view='@participations',
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
    def test_allow_modifying_the_current_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_admin.id)
        data = json.dumps(json_compatible({'role': {'token': 'WorkspaceMember'}}))

        browser.open(
            entry['@id'],
            method='PATCH',
            data=data,
            headers=http_headers(),
        )

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_admin.id)
        self.assertEqual(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'))

    @browsing
    def test_prevent_privilege_escalation(self, browser):
        self.login(self.workspace_member, browser=browser)

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        data = json.dumps(json_compatible({'role': {'token': 'WorkspaceAdmin'}}))

        with browser.expect_http_error(401):
            browser.open(
                entry['@id'],
                method='PATCH',
                data=data,
                headers=http_headers(),
            )


class TestParticipationPostWorkspace(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_let_a_user_participate(self, browser):
        self.login(self.workspace_admin, browser=browser)

        remove_participation(self.workspace, browser, self.workspace_member.id)

        browser.open(
            self.workspace,
            view='@participations',
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
            self.workspace,
            view='@participations',
            method='POST',
            data=json.dumps(data),
            headers=http_headers(),
            )

        # Posting with participant and role returns the serialized participant
        self.assertEqual(
            self.workspace_member.id,
            browser.json.get('participant').get('id'))
        self.assertEqual(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            browser.json.get('role'))

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertEqual(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

    @browsing
    def test_add_a_list_of_participants(self, browser):
        self.login(self.workspace_admin, browser=browser)

        remove_participation(self.workspace, browser, self.workspace_member.id)
        remove_participation(self.workspace, browser, self.workspace_guest.id)

        self.assertDictEqual(
            {'fridolin.hugentobler': ['WorkspaceAdmin'],
             'gunther.frohlich': ['WorkspaceAdmin']},
            self.workspace.__ac_local_roles__)

        data = {
            "participants": [
                {"participant": {"token": self.workspace_member.id},
                 "role": {"token": 'WorkspaceGuest'}},
                {"participant": self.workspace_guest.id,
                 "role": 'WorkspaceMember'}
            ]
        }

        browser.open(
            self.workspace,
            view='@participations',
            method='POST',
            data=json.dumps(data),
            headers=http_headers(),
            )

        # Posting with a list of participants returns the list of participants
        items = browser.json.get('items')
        self.assertEqual(2, len(items))

        entry = get_entry_by_id(items, self.workspace_member.id)
        self.assertEqual(
            {u'token': u'WorkspaceGuest', u'title': u'Guest'},
            entry.get('role'))

        entry = get_entry_by_id(items, self.workspace_guest.id)
        self.assertEqual(
            {u'token': u'WorkspaceMember', u'title': u'Member'},
            entry.get('role'))

        self.assertDictEqual(
            {u'beatrice.schrodinger': [u'WorkspaceGuest'],
             u'fridolin.hugentobler': [u'WorkspaceAdmin'],
             u'gunther.frohlich': [u'WorkspaceAdmin'],
             u'hans.peter': [u'WorkspaceMember']},
            self.workspace.__ac_local_roles__)

    @browsing
    def test_let_a_group_participate(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace,
            view='@participations',
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
            self.workspace,
            view='@participations',
            method='POST',
            data=json.dumps(data),
            headers=http_headers(),
            )

        browser.open(
            self.workspace,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), 'projekt_a')
        self.assertEqual(
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
                self.workspace,
                view='@participations',
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
                self.workspace,
                view='@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

    @browsing
    def test_only_one_participation_per_user_is_allowed(self, browser):
        self.login(self.workspace_admin, browser=browser)

        browser.open(
            self.workspace,
            view='@participations',
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
                self.workspace,
                view='@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

    @browsing
    def test_can_only_pass_one_of_participant_and_participants(self, browser):
        self.login(self.workspace_admin, browser=browser)

        data = {
            "participants": [
                {"participant": {"token": self.workspace_guest.id},
                 "role": {"token": 'Manager'}}
                ],
            "participant": {"token": self.workspace_member.id},
            "role": {"token": 'Manager'},
        }

        with browser.expect_http_error(400):
            browser.open(
                self.workspace,
                view='@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )
        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'one_of_participants_and_participant',
             u'translated_message': u"Cannot specify both 'participants' and "
                                    u"'participant' or 'role'",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_notifies_added_participants(self, browser):
        self.login(self.workspace_admin, browser=browser)
        data = {
            "participant": {"token": self.meeting_user.id},
            "role": {"token": 'WorkspaceGuest'},
            "notify_user": True
        }

        browser.open(self.workspace, view='@participations', method='POST',
                     data=json.dumps(data), headers=self.api_headers)
        notifications = Notification.query.all()
        self.assertEqual(1, len(notifications))
        self.assertEqual(1, Activity.query.count())
        notification = notifications[0]
        activity = notification.activity
        self.assertEqual(self.meeting_user.id, notification.userid)
        self.assertEqual(u'workspace-participation-added', activity.kind)

        data = {
            "participant": {"token": "projekt_a"},
            "role": {"token": 'WorkspaceGuest'},
            "notify_user": True
        }

        browser.open(self.workspace, view='@participations', method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual([self.meeting_user.id, self.regular_user.id, self.dossier_responsible.id],
                         sorted([notification.userid for notification in Notification.query.all()]))
        self.assertEqual([u'workspace-participation-added', u'workspace-participation-added'],
                         [activity.kind for activity in Activity.query.all()])

    @browsing
    def test_does_not_notify_participants_if_notify_user_not_set(self, browser):
        self.login(self.workspace_admin, browser=browser)
        data = {
            "participant": {"token": self.meeting_user.id},
            "role": {"token": 'WorkspaceGuest'},
        }

        browser.open(self.workspace, view='@participations', method='POST',
                     data=json.dumps(data), headers=self.api_headers)
        self.assertEqual(0, Notification.query.count())
        self.assertEqual(0, Activity.query.count())

        remove_participation(self.workspace, browser, self.meeting_user.id)
        data['notify_user'] = True
        browser.open(self.workspace, view='@participations', method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(1, Notification.query.count())
        self.assertEqual(1, Activity.query.count())


class TestParticipationPostWorkspaceFolder(IntegrationTestCase):

    @browsing
    def test_let_a_user_participate_to_a_folder(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser)
        remove_participation(self.workspace_folder, browser, self.workspace_member.id)

        browser.open(
            self.workspace_folder,
            view='@participations',
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
            self.workspace_folder,
            view='@participations',
            method='POST',
            data=json.dumps(data),
            headers=http_headers(),
            )

        browser.open(
            self.workspace_folder,
            view='@participations',
            method='GET',
            headers=http_headers(),
        )

        entry = get_entry_by_id(browser.json.get('items'), self.workspace_member.id)
        self.assertEqual(
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
                self.workspace_folder,
                view='@participations',
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
                self.workspace_folder,
                view='@participations',
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
                self.workspace_folder,
                view='@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

        self.assertEqual('BadRequest', browser.json.get('type'))
        self.assertEqual(u'invalid_role', browser.json.get('message'))
        self.assertIn('Role Manager is not available. Available roles are:',
                      browser.json.get('translated_message'))

    @browsing
    def test_do_not_allow_readding_an_already_existing_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        block_role_inheritance(self.workspace_folder, browser, copy_roles=True)

        browser.open(
            self.workspace_folder,
            view='@participations',
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
                self.workspace_folder,
                view='@participations',
                method='POST',
                data=json.dumps(data),
                headers=http_headers(),
                )

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'duplicate_participant',
             u'translated_message': u'The participant beatrice.schrodinger already exists',
             u'type': u'BadRequest'},
            browser.json)

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
                self.workspace_folder,
                view='@participations',
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
            self.portal,
            view='@my-workspace-invitations',
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
            self.portal,
            view='@my-workspace-invitations',
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
