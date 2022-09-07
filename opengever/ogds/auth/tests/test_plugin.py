from ftw.builder import Builder
from ftw.builder import create
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
