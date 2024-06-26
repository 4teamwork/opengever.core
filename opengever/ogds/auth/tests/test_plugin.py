from ftw.builder import Builder
from ftw.builder import create
from mock import patch
from opengever.ogds.auth.plugin import OGDSAuthenticationPlugin
from opengever.ogds.auth.testing import OGDSAuthTestCase
from opengever.ogds.models.service import ogds_service
from plone import api
from plone.app.testing import TEST_USER_ID
from Products.PlonePAS.plugins.group import PloneGroup
from Products.PlonePAS.plugins.ufactory import PloneUser
from zope.component import getMultiAdapter


class TestOGDSAuthPluginBase(OGDSAuthTestCase):
    """Base for test cases to test the OGDS auth plugin's interface directly.
    """

    def setUp(self):
        super(TestOGDSAuthPluginBase, self).setUp()
        self.install_ogds_plugin()

    def tearDown(self):
        super(TestOGDSAuthPluginBase, self).tearDown()
        self.uninstall_ogds_plugin()


class TestOGDSAuthPluginIUserEnumeration(TestOGDSAuthPluginBase):
    """Tests for the IUserEnumeration plugin interface.
    """

    def test_enum_users_by_id(self):
        results = self.plugin.enumerateUsers(self.regular_user.id)
        expected = ({
            'id': self.regular_user.id,
            'login': self.regular_user.getUserName(),
            'pluginid': 'ogds_auth',
        },)
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_users_by_login(self):
        results = self.plugin.enumerateUsers(login=self.regular_user.getUserName())
        expected = (self.regular_user.id, )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_id_takes_precedence_over_login(self):
        results = self.plugin.enumerateUsers(id=self.regular_user.id, login='foo')
        expected = (self.regular_user.id, )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_by_login_maps_to_username(self):
        create(
            Builder('ogds_user')
            .having(userid='12345',
                    username='charles.babbage',
                    external_id='11111111-2222-3333-4444-555555555555'))
        ogds_service().session.flush()

        results = self.plugin.enumerateUsers(login='charles.babbage')
        expected = ({
            'id': '12345',
            'login': 'charles.babbage',
            'pluginid': 'ogds_auth',
        },)
        self.assertEqual(expected, results)

    def test_enum_users_with_exact_match_true(self):
        results = self.plugin.enumerateUsers('regul', exact_match=True)
        expected = ()
        self.assertEqual(expected, results)

        results = self.plugin.enumerateUsers(self.regular_user.id, exact_match=True)
        expected = (self.regular_user.id, )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_with_exact_match_is_case_insensitive(self):
        results = self.plugin.enumerateUsers(self.regular_user.id.upper(), exact_match=True)
        expected = ({
            'id': self.regular_user.id,
            'login': self.regular_user.getUserName(),
            'pluginid': 'ogds_auth',
        },)
        self.assertEqual(expected, results)

    def test_enum_users_with_exact_match_false_does_ci_substring_search(self):
        results = self.plugin.enumerateUsers('ReGuLaR_UsE', exact_match=False)
        expected = (self.regular_user.id, )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_with_no_match_returns_empty_tuple(self):
        results = self.plugin.enumerateUsers(id='doesnt-exist')
        expected = ()
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_users_without_search_critera_returns_all_users(self):
        results = self.plugin.enumerateUsers()
        expected = (
            api.user.get('committee.secretary').getId(),
            api.user.get('james.bond').getId(),
            api.user.get('lucklicher.laser').getId(),
            self.administrator.getId(),
            api.user.get('test_user_1_').getId(),
            self.archivist.getId(),
            self.committee_responsible.getId(),
            self.dossier_manager.getId(),
            self.dossier_responsible.getId(),
            self.limited_admin.getId(),
            self.meeting_user.getId(),
            self.member_admin.getId(),
            self.propertysheets_manager.getId(),
            self.records_manager.getId(),
            self.regular_user.getId(),
            self.secretariat_user.getId(),
            self.service_user.getId(),
            self.webaction_manager.getId(),
            self.workspace_admin.getId(),
            self.workspace_guest.getId(),
            self.workspace_member.getId(),
            self.workspace_owner.getId(),
        )
        self.assertItemsEqual(expected, self.ids(results))

    def test_enum_users_with_unknown_search_criteria_returns_empty_tuple(self):
        results = self.plugin.enumerateUsers(unkown_attr='foo')
        expected = ()
        self.assertEqual(expected, results)

    def test_enum_users_attribute_search_with_exact_match_true(self):
        results = self.plugin.enumerateUsers(
            firstname='J\xc3\xbcRGEN', exact_match=True)
        expected = (
            self.archivist.getId(),
            self.secretariat_user.getId(),
        )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_attribute_search_with_exact_match_false(self):
        results = self.plugin.enumerateUsers(lastname='LER')
        expected = (
            self.committee_responsible.id,
            self.workspace_admin.id,
            self.administrator.id,
            self.dossier_responsible.id,
        )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_can_search_by_fullname_with_exact_match_true(self):
        ogds_user = ogds_service().fetch_user(self.regular_user.id)
        ogds_user.display_name = u'K\xe4thi B\xe4rfuss (FD-AFI)'
        ogds_service().session.flush()

        results = self.plugin.enumerateUsers(
            fullname='K\xc3\xa4thi B\xc3\xa4rFUSS (FD-AFI)', exact_match=True)
        expected = (self.regular_user.id, )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_can_search_by_fullname_with_exact_match_false(self):
        ogds_user = ogds_service().fetch_user(self.regular_user.id)
        ogds_user.display_name = u'K\xe4thi B\xe4rfuss (FD-AFI)'
        ogds_service().session.flush()

        results = self.plugin.enumerateUsers(fullname='THI B\xc3\xa4rFUSS')
        expected = (self.regular_user.id, )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_can_search_by_name_and_login(self):
        # Workaround to accomodate the sharing view's search for users
        results = self.plugin.enumerateUsers(name='kathi.', login='kathi.')
        expected = (self.regular_user.id, )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_supports_max_results(self):
        results = self.plugin.enumerateUsers(max_results=3)
        self.assertEqual(3, len(results))

    def test_enum_users_filters_inactive_users(self):
        # Guard assertion: User exists and is inactive
        user = ogds_service().fetch_user('inactive.user')
        self.assertFalse(user.active)

        results = self.plugin.enumerateUsers('inactive.user')
        expected = ()
        self.assertEqual(expected, results)

    def test_enum_users_returns_bytestring_values(self):
        results = self.plugin.enumerateUsers(self.regular_user.id)
        self.assertTrue(len(results) > 0)

        for key, value in results[0].items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)

    @patch('opengever.ogds.auth.plugin.OGDSAuthenticationPlugin.query_ogds',
           wraps=OGDSAuthenticationPlugin.query_ogds)
    def test_enum_users_is_cached(self, mock_query_ogds):
        self.plugin.ZCacheable_setManagerId('RAMCache')

        results = self.plugin.enumerateUsers('regular_user')
        cached_results = self.plugin.enumerateUsers('regular_user')
        self.assertEqual(results, cached_results)
        self.assertEqual(1, mock_query_ogds.call_count)

        cache_miss = self.plugin.enumerateUsers('dossier_responsible')
        self.assertNotEqual(cache_miss, cached_results)
        self.assertEqual(2, mock_query_ogds.call_count)

        negative_cache_miss = self.plugin.enumerateUsers('doesnt-exist')
        negative_cache_hit = self.plugin.enumerateUsers('doesnt-exist')
        self.assertEqual(3, mock_query_ogds.call_count)
        self.assertEqual(negative_cache_hit, negative_cache_miss)


class TestOGDSAuthPluginIGroupEnumeration(TestOGDSAuthPluginBase):
    """Tests for the IGroupEnumeration plugin interface.
    """

    def test_enum_groups_by_id(self):
        results = self.plugin.enumerateGroups('fa_users')
        expected = ({
            'id': 'fa_users',
            'pluginid': 'ogds_auth',
        },)
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_groups_with_exact_match_true(self):
        results = self.plugin.enumerateGroups('projekt', exact_match=True)
        expected = ()
        self.assertEqual(expected, results)

        results = self.plugin.enumerateGroups('projekt_a', exact_match=True)
        expected = ('projekt_a', )
        self.assertEqual(expected, self.ids(results))

    def test_enum_groups_with_exact_match_is_case_insensitive(self):
        results = self.plugin.enumerateGroups('PROJEKT_A', exact_match=True)
        expected = ('projekt_a', )
        self.assertEqual(expected, self.ids(results))

    def test_enum_groups_with_exact_match_false_does_ci_substring_search(self):
        results = self.plugin.enumerateGroups('roJEKt', exact_match=False)
        expected = (
            'projekt_a',
            'projekt_b',
            'projekt_laeaer',
        )
        self.assertEqual(expected, self.ids(results))

    def test_enum_groups_with_no_match_returns_empty_tuple(self):
        results = self.plugin.enumerateGroups(id='group-doesnt-exist')
        expected = ()
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_groups_without_search_critera_returns_all_groups(self):
        results = self.plugin.enumerateGroups()
        expected = (
            'committee_rpk_group',
            'committee_ver_group',
            'fa_inbox_users',
            'fa_users',
            'projekt_a',
            'projekt_b',
            'projekt_laeaer',
            'rk_inbox_users',
            'rk_users'
        )
        self.assertEqual(expected, self.ids(results))

    def test_enum_groups_with_unknown_search_criteria_returns_empty_tuple(self):
        results = self.plugin.enumerateGroups(unkown_attr='foo')
        expected = ()
        self.assertEqual(expected, results)

    def test_enum_groups_attribute_search_with_exact_match_true(self):
        results = self.plugin.enumerateGroups(
            title='PROJEKT A', exact_match=True)
        expected = ('projekt_a', )
        self.assertEqual(expected, self.ids(results))

    def test_enum_groups_attribute_search_with_exact_match_false(self):
        results = self.plugin.enumerateGroups(title='USERS')
        expected = (
            'fa_inbox_users',
            'fa_users',
            'rk_inbox_users',
            'rk_users',
        )
        self.assertEqual(expected, self.ids(results))

    def test_enum_groups_supports_max_results(self):
        results = self.plugin.enumerateGroups(max_results=3)
        self.assertEqual(3, len(results))

    def test_enum_groups_filters_inactive_groups(self):
        create(
            Builder('ogds_group')
            .having(groupid='inactive.group',
                    title=u'Inactive Group',
                    active=False))
        ogds_service().session.flush()

        results = self.plugin.enumerateGroups('inactive.group')
        expected = ()
        self.assertEqual(expected, results)

    def test_enum_groups_returns_bytestring_values(self):
        results = self.plugin.enumerateGroups('fa_users')
        self.assertTrue(len(results) > 0)

        for key, value in results[0].items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)

    @patch('opengever.ogds.auth.plugin.OGDSAuthenticationPlugin.query_ogds',
           wraps=OGDSAuthenticationPlugin.query_ogds)
    def test_enum_groups_is_cached(self, mock_query_ogds):
        self.plugin.ZCacheable_setManagerId('RAMCache')

        results = self.plugin.enumerateGroups('fa_users')
        cached_results = self.plugin.enumerateGroups('fa_users')
        self.assertEqual(results, cached_results)
        self.assertEqual(1, mock_query_ogds.call_count)

        cache_miss = self.plugin.enumerateGroups('projekt_a')
        self.assertNotEqual(cache_miss, cached_results)
        self.assertEqual(2, mock_query_ogds.call_count)

        negative_cache_miss = self.plugin.enumerateGroups('doesnt-exist')
        negative_cache_hit = self.plugin.enumerateGroups('doesnt-exist')
        self.assertEqual(3, mock_query_ogds.call_count)
        self.assertEqual(negative_cache_hit, negative_cache_miss)


class TestOGDSAuthPluginIGroups(TestOGDSAuthPluginBase):
    """Tests for the IGroups plugin interface.
    """

    def test_groups_for_principal(self):
        member = api.user.get(self.regular_user.id)
        results = self.plugin.getGroupsForPrincipal(member)
        expected = ('fa_users', 'projekt_a')
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_groups_for_principal_without_groups_returns_empty_tuple(self):
        member = api.user.get(self.dossier_responsible.id)
        ogds_service().fetch_user(self.dossier_responsible.id).groups = []
        ogds_service().session.flush()

        results = self.plugin.getGroupsForPrincipal(member)
        expected = ()
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_groups_for_principal_returns_bytestring_values(self):
        member = api.user.get(self.regular_user.id)
        results = self.plugin.getGroupsForPrincipal(member)

        for groupid in results:
            self.assertIsInstance(groupid, str)

    def test_groups_for_principal_filters_inactive_groups(self):
        user = ogds_service().fetch_user(self.dossier_responsible.id)
        create(
            Builder('ogds_group')
            .having(groupid='inactive.group',
                    title=u'Inactive Group',
                    active=False,
                    users=[user]))
        ogds_service().session.flush()

        member = api.user.get(self.dossier_responsible.id)
        results = self.plugin.getGroupsForPrincipal(member)
        expected = ('fa_users', 'projekt_a')
        self.assertEqual(expected, results)

    def test_groups_for_principal_filters_non_ascii_groups(self):
        user = ogds_service().fetch_user(self.dossier_responsible.id)
        create(
            Builder('ogds_group')
            .having(groupid=u'gruppe_mit_uml\xe4uten',
                    title=u'gruppe_mit_uml\xe4uten',
                    active=True,
                    users=[user]))
        ogds_service().session.flush()

        member = api.user.get(self.dossier_responsible.id)
        results = self.plugin.getGroupsForPrincipal(member)
        expected = ('fa_users', 'projekt_a')
        self.assertEqual(expected, results)

    def test_groups_for_principal_is_case_insensitive(self):
        user = PloneUser('REGULAR_USER')
        results = self.plugin.getGroupsForPrincipal(user)
        expected = ('fa_users', 'projekt_a')
        self.assertEqual(expected, results)

    def test_groups_for_principal_is_cached(self):
        kathi = self.regular_user
        robert = self.dossier_responsible
        franzi = self.committee_responsible

        user = ogds_service().fetch_user(robert.id)
        create(
            Builder('ogds_group')
            .having(groupid='additional.group',
                    users=[user]))

        ogds_service().fetch_user(franzi.id).groups = []
        ogds_service().session.flush()

        self.plugin.ZCacheable_setManagerId('RAMCache')

        with patch(
            'opengever.ogds.auth.plugin.OGDSAuthenticationPlugin.query_ogds',
                wraps=OGDSAuthenticationPlugin.query_ogds) as mock_query_ogds:

            results = self.plugin.getGroupsForPrincipal(kathi)
            cached_results = self.plugin.getGroupsForPrincipal(kathi)
            self.assertEqual(results, cached_results)
            self.assertEqual(1, mock_query_ogds.call_count)

            cache_miss = self.plugin.getGroupsForPrincipal(robert)
            self.assertNotEqual(cache_miss, cached_results)
            self.assertEqual(2, mock_query_ogds.call_count)

            negative_cache_miss = self.plugin.getGroupsForPrincipal(franzi)
            negative_cache_hit = self.plugin.getGroupsForPrincipal(franzi)
            self.assertEqual(3, mock_query_ogds.call_count)
            self.assertEqual(negative_cache_hit, negative_cache_miss)


class TestOGDSAuthPluginIGroupIntrospection(TestOGDSAuthPluginBase):
    """Tests for the IGroupIntrospection plugin interface.
    """

    def test_get_group_by_id_returns_plone_group(self):
        group = self.plugin.getGroupById('fa_users')
        self.assertIsInstance(group, PloneGroup)
        self.assertEqual(group.getProperty('title'), 'fa Users Group')
        self.assertEqual(group.getRoles(), ['Authenticated'])

    def test_get_group_by_id_for_unknown_id_returns_none(self):
        group = self.plugin.getGroupById('unknown_group')
        self.assertEqual(group, None)

    def test_get_groups_returns_list_of_plone_groups(self):
        groups = self.plugin.getGroups()
        for group in groups:
            self.assertIsInstance(group, PloneGroup)

    def test_get_group_ids_returns_list_of_group_ids(self):
        group_ids = self.plugin.getGroupIds()
        self.assertEqual(group_ids, [
            'committee_rpk_group',
            'committee_ver_group',
            'fa_inbox_users',
            'fa_users',
            'projekt_a',
            'projekt_b',
            'projekt_laeaer',
            'rk_inbox_users',
            'rk_users',
        ])

    def test_get_group_members_returns_list_of_user_ids(self):
        user_ids = self.plugin.getGroupMembers('fa_users')
        self.assertItemsEqual(user_ids, [
            api.user.get('committee.secretary').getId(),
            self.administrator.getId(),
            self.archivist.getId(),
            self.committee_responsible.getId(),
            self.dossier_manager.getId(),
            self.dossier_responsible.getId(),
            self.limited_admin.getId(),
            self.meeting_user.getId(),
            self.member_admin.getId(),
            self.propertysheets_manager.getId(),
            self.records_manager.getId(),
            self.regular_user.getId(),
            self.secretariat_user.getId(),
            self.service_user.getId(),
            self.webaction_manager.getId(),
            self.workspace_admin.getId(),
            self.workspace_guest.getId(),
            self.workspace_member.getId(),
            self.workspace_owner.getId(),
        ])

    def test_get_group_members_for_unknown_id_returns_empty_list(self):
        user_ids = self.plugin.getGroupMembers('unknown_group')
        self.assertEqual(user_ids, [])


class TestOGDSAuthPluginIPropertiesPlugin(TestOGDSAuthPluginBase):
    """Tests for the IPropertiesPlugin plugin interface.
    """

    def test_get_properties_for_user(self):
        ogds_user = ogds_service().fetch_user(self.regular_user.id)
        ogds_user.display_name = u'K\xe4thi B\xe4rfuss (FD-AFI)'
        ogds_service().session.flush()

        member = api.user.get(self.regular_user.id)
        results = self.plugin.getPropertiesForUser(member)
        expected = {
            'userid': self.regular_user.id,
            'email': 'foo@example.com',
            'firstname': 'K\xc3\xa4thi',
            'lastname': 'B\xc3\xa4rfuss',
            'fullname': 'K\xc3\xa4thi B\xc3\xa4rfuss (FD-AFI)',
        }
        self.assertEqual(expected, results)

    def test_get_properties_for_user_also_works_for_groups(self):
        group = PloneUser('projekt_a')
        group._isGroup = True
        results = self.plugin.getPropertiesForUser(group)
        expected = {
            'groupid': 'projekt_a',
            'title': 'Projekt A',
        }
        self.assertEqual(expected, results)

    def test_get_properties_for_user_with_no_match_returns_empty_dict(self):
        self.portal.acl_users.source_users.addUser(
                'some.user.id',
                'some.user.name',
                'secret')
        member_not_in_ogds = api.user.get('some.user.id')
        results = self.plugin.getPropertiesForUser(member_not_in_ogds)
        expected = {}
        self.assertEqual(expected, results)

    def test_get_properties_for_user_only_returns_props_for_active_users(self):
        ogds_user = ogds_service().fetch_user(self.dossier_responsible.id)
        ogds_user.active = False
        ogds_service().session.flush()

        inactive_member = api.user.get(self.dossier_responsible.id)
        results = self.plugin.getPropertiesForUser(inactive_member)
        expected = {}
        self.assertEqual(expected, results)

    def test_get_properties_for_user_returns_bytestring_values(self):
        member = api.user.get(self.regular_user.id)
        results = self.plugin.getPropertiesForUser(member)

        for key, value in results.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)

    def test_get_properties_for_user_replaces_none_values_with_empty_str(self):
        ogds_user = ogds_service().fetch_user(self.regular_user.id)
        ogds_user.firstname = None
        ogds_user.lastname = None
        ogds_user.display_name = None
        ogds_user.email = None
        ogds_service().session.flush()
        member = api.user.get(self.regular_user.id)

        # Note: Property values must never be `None`, otherwise the
        # propertysheet mechanism will blow up.
        results = self.plugin.getPropertiesForUser(member)
        expected = {
            'userid': self.regular_user.id,
            'email': '',
            'firstname': '',
            'lastname': '',
            'fullname': '',
        }
        self.assertEqual(expected, results)

    def test_get_properties_for_user_is_case_insensitive(self):
        user = PloneUser('REGULAR_USER')
        results = self.plugin.getPropertiesForUser(user)
        self.assertEqual(self.regular_user.id, results['userid'])

    def test_get_properties_for_user_is_cached(self):
        kathi = api.user.get(self.regular_user.id)
        robert = api.user.get(self.dossier_responsible.id)
        member_not_in_ogds = api.user.get(TEST_USER_ID)

        self.plugin.ZCacheable_setManagerId('RAMCache')

        with patch(
            'opengever.ogds.auth.plugin.OGDSAuthenticationPlugin.query_ogds',
                wraps=OGDSAuthenticationPlugin.query_ogds) as mock_query_ogds:

            results = self.plugin.getPropertiesForUser(kathi)
            cached_results = self.plugin.getPropertiesForUser(kathi)
            self.assertEqual(results, cached_results)
            self.assertEqual(1, mock_query_ogds.call_count)

            cache_miss = self.plugin.getPropertiesForUser(robert)
            self.assertNotEqual(cache_miss, cached_results)
            self.assertEqual(2, mock_query_ogds.call_count)

            negative_cache_miss = self.plugin.getPropertiesForUser(member_not_in_ogds)
            negative_cache_hit = self.plugin.getPropertiesForUser(member_not_in_ogds)
            self.assertEqual(3, mock_query_ogds.call_count)
            self.assertEqual(negative_cache_hit, negative_cache_miss)


class TestOGDSAuthPluginPloneIntegration(OGDSAuthTestCase):
    """Test case that exercises the OGDS auth plugin's methods indirectly,
    by acting on Plone and asserting on the resulting state.
    """

    def tearDown(self):
        super(TestOGDSAuthPluginPloneIntegration, self).tearDown()
        self.uninstall_ogds_plugin()

    def test_login(self):
        with self.disabled_user_plugins:
            # Guard assertion: Disabling source_users makes login fail
            with self.assertRaises(ValueError) as cm:
                self.login('kathi.barfuss')
            self.assertEqual('User could not be found', str(cm.exception))

            # With the OGDS auth plugin enabled, it should succeed
            self.install_ogds_plugin()
            self.login(self.regular_user)
            self.assertEqual(self.regular_user.id, api.user.get_current().id)
            self.logout()

    def test_get_groups(self):
        with self.disabled_group_plugins:
            # Guard assertion: Disabling IGroupsPlugins results in empty groups
            member = api.user.get(self.regular_user.id)
            self.assertEqual([], member.getGroups())

            # With the OGDS auth plugin enabled, groups should be listed
            self.install_ogds_plugin()
            member = api.user.get(self.regular_user.id)
            self.assertEqual(['projekt_a', 'fa_users'], member.getGroups())

    def test_pas_search_users_without_criteria_lists_all_users(self):
        self.install_ogds_plugin()
        pas = api.portal.get_tool('acl_users')
        users = pas.searchUsers()
        self.assertGreater(len(users), 5)
        self.assertIn(self.regular_user.id, self.ids(users))

    def test_pas_search_groups_without_criteria_lists_all_groups(self):
        self.install_ogds_plugin()
        pas = api.portal.get_tool('acl_users')
        groups = pas.searchGroups()
        self.assertGreater(len(groups), 5)
        self.assertIn('fa_users', self.ids(groups))

    def test_get_property_on_member(self):
        ogds_user = ogds_service().fetch_user(self.regular_user.id)
        ogds_user.email = u'totally.unique@example.org'
        ogds_service().session.flush()

        with self.disabled_property_plugins, self.disabled_user_plugins:
            self.install_ogds_plugin()
            user = api.user.get(self.regular_user.id)
            self.assertEqual(
                'totally.unique@example.org', user.getProperty('email'))

    def test_pas_search_by_attribute(self):
        """This covers functionality needed in og.mail.browser.inbound
        """
        ogds_user = ogds_service().fetch_user(self.regular_user.id)
        ogds_user.email = u'totally.unique@example.org'
        ogds_service().session.flush()

        with self.disabled_property_plugins, self.disabled_user_plugins:
            self.install_ogds_plugin()
            pas_search = getMultiAdapter(
                (self.portal, self.request), name='pas_search')
            matches = pas_search.searchUsers(
                email='totally.unique@example.org', exact_match=False)

            expected = [{
                'id': self.regular_user.id,
                'login': self.regular_user.getUserName(),
                'pluginid': 'ogds_auth',
                'principal_type': 'user',
                'title': 'kathi.barfuss',
                'userid': self.regular_user.id,
            }]
            self.assertEqual(expected, matches)
