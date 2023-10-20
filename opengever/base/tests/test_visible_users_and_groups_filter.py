from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.visible_users_and_groups_filter import VisibleUsersAndGroupsFilter
from opengever.ogds.models.group import Group
from opengever.testing import SolrIntegrationTestCase
import json


def clear_cache(request):
    setattr(request, VisibleUsersAndGroupsFilter.ALLOWED_USERS_AND_GROUPS_CACHEKEY, None)


class TestVisibleUsersAndGroupsFilterInGever(SolrIntegrationTestCase):

    def test_can_access_principal_is_always_possible(self):
        self.deactivate_feature('workspace')
        self.login(self.regular_user)

        self.assertFalse(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())
        self.assertTrue(VisibleUsersAndGroupsFilter().can_access_principal('example.user'))


class TestVisibleUsersAndGroupsFilterInTeamraum(SolrIntegrationTestCase):

    features = ('workspace', )

    def test_can_access_principal_is_not_possible_without_permission(self):
        self.login(self.workspace_guest)

        self.assertFalse(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())
        self.assertFalse(VisibleUsersAndGroupsFilter().can_access_principal('example.user'))

    def test_can_access_principal_is_always_possible_with_permission(self):
        self.login(self.workspace_admin)

        self.assertTrue(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())
        self.assertTrue(VisibleUsersAndGroupsFilter().can_access_principal('example.user'))

    def test_can_access_principal_is_only_possible_for_whitelisted_principals(self):
        self.login(self.workspace_guest)

        self.assertFalse(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())

        self.assertTrue(VisibleUsersAndGroupsFilter().can_access_principal(self.workspace_member.getId()))
        self.assertFalse(VisibleUsersAndGroupsFilter().can_access_principal(self.regular_user.getId()))

    def test_no_whitelisted_principals_if_not_in_any_workspace(self):
        self.login(self.regular_user)

        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 0)
        self.assertItemsEqual(
            [self.regular_user.getId()], VisibleUsersAndGroupsFilter().get_whitelisted_principals(),
            "Only the current users should be whitelisted.")

    def test_all_members_of_a_workspace_should_be_whitelisted(self):
        self.login(self.regular_user)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])

        # The regular user is now member of the project a workspace. Thus, the workspace creator should be
        # whitelisted, too.
        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 1)
        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_all_members_of_multiple_workspaces_should_be_whitelisted(self):
        self.login(self.regular_user)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            workspace_project_b = create(Builder('workspace').titled(u'Project B').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_b, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_b, self.workspace_guest.getId(), ['WorkspaceGuest'])

        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 2)
        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId(), self.workspace_guest.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_all_workspace_members_of_a_workspace_with_activated_hidden_flag_are_skipped(self):
        self.login(self.workspace_admin)

        self.assertItemsEqual(
            [self.workspace_admin.id, self.workspace_guest.id,
             self.workspace_owner.id, self.workspace_member.id],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

        self.workspace.hide_members_for_guests = True
        self.workspace.reindexObject()

        # drop cache
        delattr(self.request,
                VisibleUsersAndGroupsFilter.ALLOWED_USERS_AND_GROUPS_CACHEKEY)

        self.assertItemsEqual(
            [self.workspace_admin.id],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

        # add not hidden workspace
        workspace_project_a = create(Builder('workspace')
                                     .titled(u'Project A')
                                     .within(self.workspace_root))
        self.set_roles(workspace_project_a,
                       self.workspace_member.id, ['WorkspaceMember'])

        # drop cache
        delattr(self.request,
                VisibleUsersAndGroupsFilter.ALLOWED_USERS_AND_GROUPS_CACHEKEY)

        self.assertItemsEqual(
            [self.workspace_admin.id, self.workspace_member.id],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_members_of_other_workspaces_should_not_be_whitelisted(self):
        self.login(self.regular_user)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            workspace_project_b = create(Builder('workspace').titled(u'Project B').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_b, self.workspace_guest.getId(), ['WorkspaceGuest'])

        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 1)
        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_group_members_should_be_whitelisted(self):
        self.login(self.regular_user)
        group = Group.query.get('projekt_a')

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])

        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

        with self.login(self.workspace_admin):
            self.set_roles(workspace_project_a, group.groupid, ['WorkspaceMember'])

        clear_cache(self.request)

        self.assertItemsEqual(
            [
                self.regular_user.getId(),
                self.workspace_admin.getId(),
                group.groupid,
                self.dossier_responsible.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_whitelisted_principals_are_cached_per_request(self):
        self.login(self.regular_user)

        self.assertItemsEqual(
            [self.regular_user.getId()], VisibleUsersAndGroupsFilter().get_whitelisted_principals())

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])

        self.assertItemsEqual(
            [self.regular_user.getId()], VisibleUsersAndGroupsFilter().get_whitelisted_principals())

        clear_cache(self.request)

        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    @browsing
    def test_protect_actors_user_lookup(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal.absolute_url() + '/@actors/' + self.workspace_admin.getId(), headers=self.api_headers)

        self.assertDictEqual(
            {
                u'@id': 'http://nohost/plone/@actors/workspace_admin',
                u'@type': u'virtual.ogds.actor',
                u'active': False,
                u'actor_type': u'null',
                u'identifier': u'workspace_admin',
                u'is_absent': False,
                u'portrait_url': None,
                u'label': u'Unknown ID',
                u'representatives': [],
                u'represents': None,
            },
            browser.json,
        )

        with self.login(self.workspace_admin):
            self.set_roles(self.workspace, self.regular_user.getId(), ['WorkspaceMember'])

        browser.open(self.portal.absolute_url() + '/@actors/' + self.workspace_admin.getId(), headers=self.api_headers)

        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/@actors/workspace_admin',
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'user',
                u'identifier': u'workspace_admin',
                u'is_absent': False,
                u'label': u'Hugentobler Fridolin',
                u'portrait_url': None,
                u'representatives': [{u'@id': u'http://nohost/plone/@actors/workspace_admin',
                                      u'identifier': u'workspace_admin'}],
                u'represents': {u'@id': u'http://nohost/plone/@ogds-users/fridolin.hugentobler'}
            },
            browser.json,
        )

    @browsing
    def test_protect_actors_group_lookup(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal.absolute_url() + '/@actors/projekt_a', headers=self.api_headers)

        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/@actors/projekt_a',
                u'@type': u'virtual.ogds.actor',
                u'active': False,
                u'actor_type': u'null',
                u'identifier': u'projekt_a',
                u'is_absent': False,
                u'label': u'Unknown ID',
                u'portrait_url': None,
                u'representatives': [],
                u'represents': None
            },
            browser.json,
        )

        with self.login(self.workspace_admin):
            self.set_roles(self.workspace, 'projekt_a', ['WorkspaceMember'])

        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/@actors/projekt_a',
                u'@type': u'virtual.ogds.actor',
                u'active': False,
                u'actor_type': u'null',
                u'identifier': u'projekt_a',
                u'is_absent': False,
                u'label': u'Unknown ID',
                u'portrait_url': None,
                u'representatives': [],
                u'represents': None
            },
            browser.json,
        )

    @browsing
    def test_protect_actors_list_lookup(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.portal.absolute_url() + '/@actors',
            method="POST",
            data=json.dumps({'actor_ids': [self.workspace_admin.getId()]}),
            headers=self.api_headers)

        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/@actors',
                u'items': [
                    {u'@id': u'http://nohost/plone/@actors/workspace_admin',
                     u'@type': u'virtual.ogds.actor',
                     u'active': False,
                     u'actor_type': u'null',
                     u'identifier': u'workspace_admin',
                     u'is_absent': False,
                     u'label': u'Unknown ID',
                     u'portrait_url': None,
                     u'representatives': [],
                     u'represents': None}
                ]
            },
            browser.json,
        )

        with self.login(self.workspace_admin):
            self.set_roles(self.workspace, self.regular_user.getId(), ['WorkspaceMember'])

        browser.open(
            self.portal.absolute_url() + '/@actors',
            method="POST",
            data=json.dumps({'actor_ids': [self.workspace_admin.getId()]}),
            headers=self.api_headers)

        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/@actors',
                u'items': [
                    {u'@id': u'http://nohost/plone/@actors/workspace_admin',
                     u'@type': u'virtual.ogds.actor',
                     u'active': True,
                     u'actor_type': u'user',
                     u'identifier': u'workspace_admin',
                     u'is_absent': False,
                     u'label': u'Hugentobler Fridolin',
                     u'portrait_url': None,
                     u'representatives': [{u'@id': u'http://nohost/plone/@actors/workspace_admin',
                                           u'identifier': u'workspace_admin'}],
                     u'represents': {u'@id': u'http://nohost/plone/@ogds-users/fridolin.hugentobler'}}
                ]
            },
            browser.json,
        )

    @browsing
    def test_protect_lookup_user(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(self.portal.absolute_url() + '/@users/' + self.workspace_admin.getId(),headers=self.api_headers)

        with self.login(self.workspace_admin):
            self.set_roles(self.workspace, self.regular_user.getId(), ['WorkspaceMember'])

        browser.open(self.portal.absolute_url() + '/@users/' + self.workspace_admin.getId(),headers=self.api_headers)

        self.assertEqual(u'Hugentobler Fridolin', browser.json.get('fullname'))

    @browsing
    def test_enumarating_users_without_permission_is_not_possible(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open('{}/@users'.format(self.portal.absolute_url()),
                         headers=self.api_headers)

    @browsing
    def test_query_users_without_permission_is_not_possible(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open('{}/@users?query=max.muster'.format(self.portal.absolute_url()),
                         headers=self.api_headers)

    @browsing
    def test_protect_lookup_ogds_user(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(self.portal.absolute_url() + '/@ogds-users/' + self.workspace_admin.getId(),headers=self.api_headers)

        with self.login(self.workspace_admin):
            self.set_roles(self.workspace, self.regular_user.getId(), ['WorkspaceMember'])

        browser.open(self.portal.absolute_url() + '/@ogds-users/' + self.workspace_admin.getId(),headers=self.api_headers)

        self.assertEqual(u'Fridolin', browser.json.get('firstname'))

    @browsing
    def test_do_not_expose_groups_for_users_without_permission(self, browser):
        self.login(self.workspace_guest, browser)

        browser.open(self.portal.absolute_url() + '/@ogds-users/' + self.workspace_guest.getId(),headers=self.api_headers)

        self.assertEqual([], browser.json.get('groups'))

        self.login(self.workspace_admin, browser)

        browser.open(self.portal.absolute_url() + '/@ogds-users/' + self.workspace_guest.getId(),headers=self.api_headers)

        self.assertEqual(1, len(browser.json.get('groups')))

    @browsing
    def test_groups_endpoint_is_not_available_for_teamraum_users(self, browser):
        self.login(self.workspace_admin, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.portal.absolute_url() + '/@groups/projekt_a', headers=self.api_headers)

        self.login(self.workspace_member, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.portal.absolute_url() + '/@groups/projekt_a', headers=self.api_headers)

        self.login(self.workspace_guest, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.portal.absolute_url() + '/@groups/projekt_a', headers=self.api_headers)

        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.portal.absolute_url() + '/@groups/projekt_a', headers=self.api_headers)

    @browsing
    def test_ogds_user_listing_only_returns_whitelisted_users(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.portal.absolute_url() + '/@ogds-user-listing', headers=self.api_headers)

        self.assertItemsEqual(
            [
                self.regular_user.getId(),
            ],
            [user.get('userid') for user in browser.json.get('items')]
        )

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, self.workspace_guest.getId(), ['WorkspaceGuest'])

        browser.open(self.portal.absolute_url() + '/@ogds-user-listing', headers=self.api_headers)

        self.assertItemsEqual(
            [
                self.regular_user.getId(),
                self.workspace_admin.getId(),
                self.workspace_guest.getId(),
            ],
            [user.get('userid') for user in browser.json.get('items')]
        )

    @browsing
    def test_ogds_group_listing_only_returns_whitelisted_groups(self, browser):
        self.login(self.regular_user, browser)
        group = Group.query.get('projekt_a')

        browser.open(self.portal.absolute_url() + '/@ogds-group-listing', headers=self.api_headers)

        self.assertItemsEqual(
            [],
            [user.get('group') for user in browser.json.get('items')]
        )

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, group.groupid, ['WorkspaceGuest'])

        browser.open(self.portal.absolute_url() + '/@ogds-group-listing', headers=self.api_headers)

        self.assertItemsEqual(
            [
                group.groupid
            ],
            [user.get('groupid') for user in browser.json.get('items')]
        )

    @browsing
    def test_protect_lookup_ogds_groups(self, browser):
        self.login(self.regular_user, browser)
        group = Group.query.get('projekt_a')

        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(self.portal.absolute_url() + '/@ogds-groups/' + group.groupid,headers=self.api_headers)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, group.groupid, ['WorkspaceMember'])

        browser.open(self.portal.absolute_url() + '/@ogds-groups/' + group.groupid,headers=self.api_headers)

        self.assertEqual(u'Projekt A', browser.json.get('title'))
