from ftw.builder import Builder
from ftw.builder import create
from mock import patch
from opengever.ogds.auth.plugin import OGDSAuthenticationPlugin
from opengever.ogds.auth.testing import OGDSAuthTestCase
from opengever.ogds.models.service import ogds_service
from plone import api


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
        results = self.plugin.enumerateUsers('kathi.barfuss')
        expected = ({
            'id': 'kathi.barfuss',
            'login': 'kathi.barfuss',
            'pluginid': 'ogds_auth',
        },)
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_users_by_login(self):
        results = self.plugin.enumerateUsers(login='kathi.barfuss')
        expected = ('kathi.barfuss', )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_id_takes_precedence_over_login(self):
        results = self.plugin.enumerateUsers(id='kathi.barfuss', login='foo')
        expected = ('kathi.barfuss', )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_with_exact_match_true(self):
        results = self.plugin.enumerateUsers('kathi', exact_match=True)
        expected = ()
        self.assertEqual(expected, results)

        results = self.plugin.enumerateUsers('kathi.barfuss', exact_match=True)
        expected = ('kathi.barfuss', )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_with_exact_match_false_does_ci_substring_search(self):
        results = self.plugin.enumerateUsers('atHI.BArfu', exact_match=False)
        expected = ('kathi.barfuss', )
        self.assertEqual(expected, self.ids(results))

    def test_enum_users_with_no_match_returns_empty_tuple(self):
        results = self.plugin.enumerateUsers(id='doesnt-exist')
        expected = ()
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_users_without_search_critera_returns_all_users(self):
        results = self.plugin.enumerateUsers()
        expected = (
            'beatrice.schrodinger',
            'committee.secretary',
            'david.meier',
            'faivel.fruhling',
            'franzi.muller',
            'fridolin.hugentobler',
            'gunther.frohlich',
            'hans.peter',
            'herbert.jager',
            'james.bond',
            'jurgen.fischer',
            'jurgen.konig',
            'kathi.barfuss',
            'lucklicher.laser',
            'maja.harzig',
            'nicole.kohler',
            'propertysheets.manager',
            'ramon.flucht',
            'robert.ziegler',
            'service.user',
            'webaction.manager',
        )
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
        results = self.plugin.enumerateUsers('kathi.barfuss')
        self.assertTrue(len(results) > 0)

        for key, value in results[0].items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)

    @patch('opengever.ogds.auth.plugin.OGDSAuthenticationPlugin.query_ogds',
           wraps=OGDSAuthenticationPlugin.query_ogds)
    def test_enum_users_is_cached(self, mock_query_ogds):
        self.plugin.ZCacheable_setManagerId('RAMCache')

        results = self.plugin.enumerateUsers('kathi.barfuss')
        cached_results = self.plugin.enumerateUsers('kathi.barfuss')
        self.assertEqual(results, cached_results)
        self.assertEqual(1, mock_query_ogds.call_count)

        cache_miss = self.plugin.enumerateUsers('robert.ziegler')
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
        member = api.user.get('kathi.barfuss')
        results = self.plugin.getGroupsForPrincipal(member)
        expected = ('fa_users', 'projekt_a')
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_groups_for_principal_without_groups_returns_empty_tuple(self):
        member = api.user.get('robert.ziegler')
        ogds_service().fetch_user('robert.ziegler').groups = []
        ogds_service().session.flush()

        results = self.plugin.getGroupsForPrincipal(member)
        expected = ()
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_groups_for_principal_returns_bytestring_values(self):
        member = api.user.get('kathi.barfuss')
        results = self.plugin.getGroupsForPrincipal(member)

        for groupid in results:
            self.assertIsInstance(groupid, str)

    def test_groups_for_principal_filters_inactive_groups(self):
        user = ogds_service().fetch_user('robert.ziegler')
        create(
            Builder('ogds_group')
            .having(groupid='inactive.group',
                    title=u'Inactive Group',
                    active=False,
                    users=[user]))
        ogds_service().session.flush()

        member = api.user.get('robert.ziegler')
        results = self.plugin.getGroupsForPrincipal(member)
        expected = ('fa_users', 'projekt_a')
        self.assertEqual(expected, results)

    @patch('opengever.ogds.auth.plugin.OGDSAuthenticationPlugin.query_ogds',
           wraps=OGDSAuthenticationPlugin.query_ogds)
    def test_groups_for_principal_is_cached(self, mock_query_ogds):
        kathi = api.user.get('kathi.barfuss')
        robert = api.user.get('robert.ziegler')
        franzi = api.user.get('franzi.muller')

        user = ogds_service().fetch_user('robert.ziegler')
        create(
            Builder('ogds_group')
            .having(groupid='additional.group',
                    users=[user]))

        ogds_service().fetch_user('franzi.muller').groups = []
        ogds_service().session.flush()

        self.plugin.ZCacheable_setManagerId('RAMCache')

        # An initial call to getGroupsForPrincipal(user) leads to recursive
        # calls to getGroupsForPrincipal(group), via the 'recursive_groups'
        # groupmaker plugin - I have a strong feeling we'll want to turn this
        # off, since we already store flattened user -> group memberships in
        # OGDS, and don't store group -> group memberships anyway.
        #
        # For now however, we'll just have to be a bit more deliberate about
        # tracking call counts in this test.

        calls_before = mock_query_ogds.call_count
        results = self.plugin.getGroupsForPrincipal(kathi)
        cached_results = self.plugin.getGroupsForPrincipal(kathi)
        self.assertEqual(results, cached_results)
        self.assertEqual(1, mock_query_ogds.call_count - calls_before)

        calls_before = mock_query_ogds.call_count
        cache_miss = self.plugin.getGroupsForPrincipal(robert)
        self.assertNotEqual(cache_miss, cached_results)
        self.assertEqual(1, mock_query_ogds.call_count - calls_before)

        calls_before = mock_query_ogds.call_count
        negative_cache_miss = self.plugin.getGroupsForPrincipal(franzi)
        negative_cache_hit = self.plugin.getGroupsForPrincipal(franzi)
        self.assertEqual(1, mock_query_ogds.call_count - calls_before)
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
            self.login('kathi.barfuss')
            self.assertEqual('kathi.barfuss', api.user.get_current().getId())
            self.logout()

    def test_get_groups(self):
        with self.disabled_group_plugins:
            # Guard assertion: Disabling IGroupsPlugins results in empty groups
            member = api.user.get('kathi.barfuss')
            self.assertEqual([], member.getGroups())

            # With the OGDS auth plugin enabled, groups should be listed
            self.install_ogds_plugin()
            member = api.user.get('kathi.barfuss')
            self.assertEqual(['projekt_a', 'fa_users'], member.getGroups())

    def test_pas_search_users_without_criteria_lists_all_users(self):
        self.install_ogds_plugin()
        pas = api.portal.get_tool('acl_users')
        users = pas.searchUsers()
        self.assertGreater(len(users), 5)
        self.assertIn('kathi.barfuss', self.ids(users))

    def test_pas_search_groups_without_criteria_lists_all_groups(self):
        self.install_ogds_plugin()
        pas = api.portal.get_tool('acl_users')
        groups = pas.searchGroups()
        self.assertGreater(len(groups), 5)
        self.assertIn('fa_users', self.ids(groups))