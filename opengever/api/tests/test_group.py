from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.api.group import ASSIGNABLE_ROLES
from opengever.base.exceptions import IncorrectConfigurationError
from opengever.base.utils import check_group_plugin_configuration
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin
from Products.PlonePAS.interfaces.group import IGroupIntrospection
from Products.PlonePAS.interfaces.group import IGroupManagement
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from unittest import expectedFailure
import json


class TestCheckGroupPluginConfiguration(IntegrationTestCase):

    def test_raises_if_source_group_not_in_group_management_plugins(self):
        self.login(self.regular_user)
        check_group_plugin_configuration(self.portal)

        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        plugins.deactivatePlugin(IGroupManagement, 'source_groups')

        with self.assertRaises(IncorrectConfigurationError) as exc:
            check_group_plugin_configuration(self.portal)

        self.assertEqual(
            'Configuration error: source_groups plugin is not active '
            'for group management.',
            exc.exception.message)

    def test_raises_if_source_group_not_in_groups_plugin(self):
        self.login(self.regular_user)
        check_group_plugin_configuration(self.portal)

        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        plugins.deactivatePlugin(IGroupsPlugin, 'source_groups')

        with self.assertRaises(IncorrectConfigurationError) as exc:
            check_group_plugin_configuration(self.portal)

        self.assertEqual(
            'Configuration error: source_groups plugin is not active '
            'for the groups plugin.',
            exc.exception.message)

    def test_raises_if_source_group_not_first_group_management_plugin(self):
        self.login(self.regular_user)
        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        manage_addPloneLDAPMultiPlugin(
            acl_users, "ldap", title="title", login_attr="uid",
            uid_attr="mail", users_base="ou=Users", users_scope=0,
            roles="CustomRole", groups_base="ou=Groups", groups_scope=1,
            binduid="cn=admin", bindpwd="XXX", rdn_attr="cn", LDAP_server=None
            )
        plugins.activatePlugin(IGroupManagement, 'ldap')
        plugins.movePluginsUp(IGroupManagement, ('ldap',))

        with self.assertRaises(IncorrectConfigurationError) as exc:
            check_group_plugin_configuration(self.portal)

        self.assertEqual(
            'Configuration error: source_groups plugin needs to be the first '
            'group management plugin.',
            exc.exception.message)

    def test_raises_if_source_group_not_in_group_enumeration_plugins(self):
        self.login(self.regular_user)
        check_group_plugin_configuration(self.portal)

        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        plugins.deactivatePlugin(IGroupEnumerationPlugin, 'source_groups')

        with self.assertRaises(IncorrectConfigurationError) as exc:
            check_group_plugin_configuration(self.portal)

        self.assertEqual(
            'Configuration error: source_groups plugin is not active '
            'for group enumeration.',
            exc.exception.message)

    def test_raises_if_source_group_not_in_group_introspection_plugins(self):
        self.login(self.regular_user)
        check_group_plugin_configuration(self.portal)

        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        plugins.deactivatePlugin(IGroupIntrospection, 'source_groups')

        with self.assertRaises(IncorrectConfigurationError) as exc:
            check_group_plugin_configuration(self.portal)

        self.assertEqual(
            'Configuration error: source_groups plugin is not active '
            'for group introspection.',
            exc.exception.message)


class TestGroupGet(IntegrationTestCase):

    @browsing
    def test_fetch_groups_is_allowed_for_administrators(self, browser):
        self.login(self.workspace_owner, browser)

        with browser.expect_unauthorized():
            browser.open(
                self.portal,
                view='@groups',
                method='GET',
                headers=self.api_headers)

        self.login(self.administrator, browser)
        response = browser.open(
            self.portal,
            view='@groups',
            method='GET',
            headers=self.api_headers)

        self.assertEqual(200, response.status_code)


class TestGroupPost(IntegrationTestCase):

    @browsing
    def test_group_creation_is_allowed_for_administrators(self, browser):
        self.login(self.workspace_owner, browser)
        portal_groups = getToolByName(self.portal, "portal_groups")

        self.groupid = u'test_group'
        self.assertIsNone(portal_groups.getGroupById(self.groupid))

        payload = {
            u'groupname': self.groupid,
        }

        with browser.expect_unauthorized():
            browser.open(
                self.portal,
                view='@groups',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertIsNone(portal_groups.getGroupById(self.groupid))

        self.login(self.administrator, browser)
        response = browser.open(
            self.portal,
            view='@groups',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)
        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/@groups/test_group',
             u'@type': u'virtual.plone.group',
             u'description': None,
             u'email': None,
             u'groupname': u'test_group',
             u'id': u'test_group',
             u'roles': [u'Authenticated'],
             u'title': None,
             u'users': {u'@id': u'http://nohost/plone/@groups',
                        u'items': [],
                        u'items_total': 0}},
            response.json
            )
        self.assertIsNotNone(portal_groups.getGroupById(self.groupid))

    @browsing
    def test_group_creation_adds_it_in_the_ogds(self, browser):
        self.login(self.manager, browser)

        ogds_group = Group.query.get('test_group')
        self.assertIsNone(ogds_group)

        payload = {
            u'groupname': u'test_group',
            u'title': u'Test group',
            u'users': [self.workspace_guest.getId(), self.workspace_member.getId()]
        }
        response = browser.open(
            self.portal,
            view='@groups',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)
        ogds_group = Group.query.get('test_group')
        self.assertIsNotNone(ogds_group)
        self.assertTrue(ogds_group.is_local)
        self.assertTrue(ogds_group.active)
        self.assertEqual('Test group', ogds_group.title)
        self.assertItemsEqual(
            [User.query.get(self.workspace_guest.getId()),
             User.query.get(self.workspace_member.getId())],
            ogds_group.users)

    @browsing
    def test_cannot_create_group_that_already_exists_in_ogds(self, browser):
        self.login(self.manager, browser)

        ogds_group = Group.query.get('projekt_a')
        self.assertIsNotNone(ogds_group)

        payload = {
            u'groupname': 'projekt_a',
        }
        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@groups',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            'Group projekt_a already exists in OGDS.')
        self.assertEqual(browser.json[u'type'], u'BadRequest')

    @browsing
    def test_group_creation_fails_when_assigning_dissallowed_roles(self, browser):
        self.login(self.manager, browser)

        roles = ['Administrator']
        self.assertNotIn(roles[0], ASSIGNABLE_ROLES)

        payload = {
            u'groupname': u'test_group',
            u'roles': roles
        }
        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@groups',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            'Role Administrator cannot be assigned. Permitted '
            'roles are: workspace_guest, workspace_member, workspace_admin')
        self.assertEqual(browser.json[u'type'], u'BadRequest')

    @browsing
    def test_group_creation_fails_when_assigning_user_not_in_ogds(self, browser):
        self.login(self.manager, browser)

        payload = {
            u'groupname': u'test_group',
            u'users': ['unknown']
        }
        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@groups',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            "User unknown not found in OGDS.")
        self.assertEqual(browser.json[u'type'], u'BadRequest')

    @browsing
    def test_group_creation_fails_if_groupname_is_too_long(self, browser):
        self.login(self.manager, browser)
        groupid = 256*"a"
        ogds_group = Group.query.get(groupid)
        self.assertIsNone(ogds_group)

        payload = {
            u'groupname': groupid,
        }
        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@groups',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            u'The group name you entered is too long: maximal length is 255')
        self.assertEqual(browser.json[u'type'], u'BadRequest')
        ogds_group = Group.query.get(groupid)
        self.assertIsNone(ogds_group)

    @browsing
    def test_group_creation_fails_if_configuration_is_incorrect(self, browser):
        self.login(self.manager, browser)
        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        plugins.deactivatePlugin(IGroupManagement, 'source_groups')

        portal_groups = getToolByName(self.portal, "portal_groups")
        self.groupid = u'test_group'

        self.assertIsNone(portal_groups.getGroupById(self.groupid))

        payload = {
            u'groupname': self.groupid,
        }

        with browser.expect_http_error(500):
            browser.open(
                self.portal,
                view='@groups',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            u'Configuration error: source_groups plugin is not active for '
            u'group management.')
        self.assertEqual(browser.json[u'type'], u'IncorrectConfigurationError')
        self.assertIsNone(portal_groups.getGroupById(self.groupid))


class TestGeverGroupsPatch(IntegrationTestCase):

    def setUp(self):
        super(TestGeverGroupsPatch, self).setUp()
        self.groupid = u'committee_rpk_group'
        self.ogds_group = Group.query.get(self.groupid)
        self.ogds_group.is_local = True

    @expectedFailure
    @browsing
    def test_updating_group_is_allowed_for_administrators(self, browser):
        self.login(self.workspace_owner, browser)

        portal_groups = getToolByName(self.portal, "portal_groups")

        group_data = portal_groups.getGroupById(self.groupid)
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission',
                         safe_unicode(group_data.getGroupTitleOrName()))
        self.assertItemsEqual(['Authenticated'], group_data.getRoles())
        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id],
            [user.getId() for user in group_data.getGroupMembers()])

        payload = {
            u'title': u'new title',
            u'roles': ['workspace_guest'],
            u'users': {self.workspace_guest.getId(): True},
        }
        with browser.expect_unauthorized():
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                data=json.dumps(payload),
                method='PATCH',
                headers=self.api_headers)

        group_data = portal_groups.getGroupById(self.groupid)
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission',
                         safe_unicode(group_data.getGroupTitleOrName()))
        self.assertItemsEqual(['Authenticated'], group_data.getRoles())
        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id],
            [user.getId() for user in group_data.getGroupMembers()])

        self.login(self.administrator, browser)
        response = browser.open(
            "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
            data=json.dumps(payload),
            method='PATCH',
            headers=self.api_headers)

        group_data = portal_groups.getGroupById(self.groupid)
        self.assertEqual(204, response.status_code)
        self.assertEqual(u'new title',
                         safe_unicode(group_data.getGroupTitleOrName()))
        self.assertItemsEqual(['Authenticated', 'workspace_guest'],
                              group_data.getRoles())
        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id, self.workspace_guest.id],
            [user.getId() for user in group_data.getGroupMembers()])

    @browsing
    def test_group_update_fails_if_configuration_is_incorrect(self, browser):
        self.login(self.administrator, browser)
        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        plugins.deactivatePlugin(IGroupManagement, 'source_groups')

        portal_groups = getToolByName(self.portal, "portal_groups")
        group_data = portal_groups.getGroupById(self.groupid)
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission',
                         safe_unicode(group_data.getGroupTitleOrName()))

        payload = {u'title': u'new title'}
        with browser.expect_http_error(500):
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                data=json.dumps(payload),
                method='PATCH',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            u'Configuration error: source_groups plugin is not active for '
            u'group management.')
        self.assertEqual(browser.json[u'type'], u'IncorrectConfigurationError')
        group_data = portal_groups.getGroupById(self.groupid)
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission',
                         safe_unicode(group_data.getGroupTitleOrName()))

    @expectedFailure
    @browsing
    def test_updating_group_also_updates_ogds(self, browser):
        self.login(self.administrator, browser)

        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission', self.ogds_group.title)
        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id],
            [user.userid for user in self.ogds_group.users])

        payload = {
            u'title': u'new title',
            u'roles': ['workspace_guest'],
            u'users': {self.workspace_guest.getId(): True},
        }

        response = browser.open(
            "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
            data=json.dumps(payload),
            method='PATCH',
            headers=self.api_headers)

        self.assertEqual(204, response.status_code)
        self.assertEqual(u'new title', self.ogds_group.title)
        self.ogds_group.session.expire(self.ogds_group)
        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id, self.workspace_guest.id],
            [user.userid for user in self.ogds_group.users])

    @browsing
    def test_all_users_can_be_removed_from_ogds_group(self, browser):
        self.login(self.administrator, browser)

        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id],
            [user.userid for user in self.ogds_group.users])

        payload = {u'users': {self.committee_responsible.id: False,
                              self.administrator.id: False}}

        response = browser.open(
            "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
            data=json.dumps(payload),
            method='PATCH',
            headers=self.api_headers)

        self.ogds_group.session.expire(self.ogds_group)
        self.assertEqual(204, response.status_code)
        self.assertEqual([], self.ogds_group.users)

    @browsing
    def test_does_not_override_title_when_no_title_and_no_description_are_set(self, browser):
        self.login(self.administrator, browser)

        portal_groups = getToolByName(self.portal, "portal_groups")
        group_data = portal_groups.getGroupById(self.groupid)
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission',
                         safe_unicode(group_data.getProperty('title')))

        payload = {'users': {self.workspace_guest.getId(): True}}
        browser.open("{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                     data=json.dumps(payload), method='PATCH', headers=self.api_headers)

        group_data = portal_groups.getGroupById(self.groupid)
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission',
                         safe_unicode(group_data.getProperty('title')))

    @browsing
    def test_only_local_groups_can_be_updated(self, browser):
        self.login(self.administrator, browser)
        self.ogds_group.is_local = False
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission', self.ogds_group.title)

        payload = {
            u'title': u'new title',
        }
        with browser.expect_http_error(400):
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                data=json.dumps(payload),
                method='PATCH',
                headers=self.api_headers)

        self.assertEqual({u'message': u'Can only modify local groups.',
                          u'type': u'BadRequest'},
                         browser.json)
        self.assertEqual(u'Gruppe Rechnungspr\xfcfungskommission', self.ogds_group.title)

    @browsing
    def test_cannot_update_group_with_disallowed_roles(self, browser):
        self.login(self.manager, browser)

        roles = ['Administrator']
        self.assertNotIn(roles[0], ASSIGNABLE_ROLES)

        payload = {
            u'roles': roles
        }
        with browser.expect_http_error(400):
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                data=json.dumps(payload),
                method='PATCH',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            'Role Administrator cannot be assigned. Permitted '
            'roles are: workspace_guest, workspace_member, workspace_admin')
        self.assertEqual(browser.json[u'type'], u'BadRequest')

    @browsing
    def test_cannot_update_group_with_user_not_in_ogds(self, browser):
        self.login(self.manager, browser)
        userid = 'not_in_ogds'
        create(Builder('user').with_userid(userid))

        payload = {
            u'users': {userid: True}
        }
        with browser.expect_http_error(400):
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                data=json.dumps(payload),
                method='PATCH',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            "Users ['{}'] not found in OGDS.".format(userid))
        self.assertEqual(browser.json[u'type'], u'BadRequest')
        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id],
            [user.userid for user in self.ogds_group.users])

        create(Builder('ogds_user').id(userid))
        browser.open(
            "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
            data=json.dumps(payload),
            method='PATCH',
            headers=self.api_headers)
        self.ogds_group.session.expire(self.ogds_group)
        self.assertItemsEqual(
            [self.committee_responsible.id, self.administrator.id, userid],
            [user.userid for user in self.ogds_group.users])


class TestGeverGroupsDelete(IntegrationTestCase):

    def setUp(self):
        super(TestGeverGroupsDelete, self).setUp()
        self.groupid = u'committee_rpk_group'
        self.ogds_group = Group.query.get(self.groupid)
        self.ogds_group.is_local = True

    @browsing
    def test_deleting_group_is_allowed_for_administrators(self, browser):
        self.login(self.workspace_owner, browser)
        portal_groups = getToolByName(self.portal, "portal_groups")
        self.assertIsNotNone(portal_groups.getGroupById(self.groupid))

        with browser.expect_unauthorized():
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                method='DELETE',
                headers=self.api_headers)

        self.login(self.administrator, browser)
        response = browser.open(
            "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
            method='DELETE',
            headers=self.api_headers)

        self.assertEqual(204, response.status_code)
        self.assertIsNone(portal_groups.getGroupById(self.groupid))

    @browsing
    def test_deleting_group_fails_if_configuration_is_incorrect(self, browser):
        self.login(self.administrator, browser)
        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        plugins.deactivatePlugin(IGroupManagement, 'source_groups')

        portal_groups = getToolByName(self.portal, "portal_groups")
        self.assertIsNotNone(portal_groups.getGroupById(self.groupid))

        with browser.expect_http_error(500):
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                method='DELETE',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            u'Configuration error: source_groups plugin is not active for '
            u'group management.')
        self.assertEqual(browser.json[u'type'], u'IncorrectConfigurationError')
        self.assertIsNotNone(portal_groups.getGroupById(self.groupid))

    @browsing
    def test_deleting_group_updates_ogds(self, browser):
        self.login(self.administrator, browser)
        portal_groups = getToolByName(self.portal, "portal_groups")

        self.assertIsNotNone(portal_groups.getGroupById(self.groupid))
        self.assertTrue(self.ogds_group.active)

        browser.open(
            "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
            method='DELETE',
            headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertIsNone(portal_groups.getGroupById(self.groupid))
        self.assertFalse(self.ogds_group.active)

    @browsing
    def test_only_local_groups_can_be_deleted(self, browser):
        self.login(self.administrator, browser)
        portal_groups = getToolByName(self.portal, "portal_groups")
        self.ogds_group.is_local = False
        self.assertIsNotNone(portal_groups.getGroupById(self.groupid))

        with browser.expect_http_error(400):
            browser.open(
                "{}/@groups/{}".format(self.portal.absolute_url(), self.groupid),
                method='DELETE',
                headers=self.api_headers)

        self.assertEqual({u'message': u'Can only delete local groups.',
                          u'type': u'BadRequest'},
                         browser.json)
        self.assertIsNotNone(portal_groups.getGroupById(self.groupid))
