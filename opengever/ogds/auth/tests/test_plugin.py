from opengever.ogds.auth.testing import OGDSAuthTestCase
from opengever.ogds.models.service import ogds_service
from plone import api


def ids(sequence):
    return tuple((item['id'] for item in sequence))


class TestOGDSAuthPlugin(OGDSAuthTestCase):
    """Test case that tests the OGDS auth plugin's interface directly.
    """

    def setUp(self):
        super(TestOGDSAuthPlugin, self).setUp()
        self.install_ogds_plugin()

    def tearDown(self):
        super(TestOGDSAuthPlugin, self).tearDown()
        self.uninstall_ogds_plugin()

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
        self.assertEqual(expected, ids(results))

    def test_enum_users_id_takes_precedence_over_login(self):
        results = self.plugin.enumerateUsers(id='kathi.barfuss', login='foo')
        expected = ('kathi.barfuss', )
        self.assertEqual(expected, ids(results))

    def test_enum_users_with_no_match_returns_empty_tuple(self):
        results = self.plugin.enumerateUsers(id='doesnt-exist')
        expected = ()
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_users_without_id_or_login_returns_empty_tuple(self):
        results = self.plugin.enumerateUsers()
        expected = ()
        self.assertEqual(expected, results)
        self.assertIsInstance(results, tuple)

    def test_enum_users_returns_bytestring_values(self):
        results = self.plugin.enumerateUsers('kathi.barfuss')
        self.assertTrue(len(results) > 0)

        for key, value in results[0].items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)

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
