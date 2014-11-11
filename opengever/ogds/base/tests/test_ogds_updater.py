from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.tests.ldaphelpers import FakeLDAPPlugin
from opengever.ogds.base.tests.ldaphelpers import FakeLDAPSearchUtility
from opengever.ogds.base.tests.ldaphelpers import FakeLDAPUserFolder
from opengever.ogds.base.utils import ogds_service
from opengever.testing import FunctionalTestCase
from zope.component import provideAdapter


FAKE_LDAP_USERFOLDER = FakeLDAPUserFolder()


class TestOGDSUpdater(FunctionalTestCase):

    def setUp(self):
        super(TestOGDSUpdater, self).setUp()
        self.portal = self.layer['portal']

        ldap_plugin = FakeLDAPPlugin(FAKE_LDAP_USERFOLDER)
        self.portal.acl_users._setObject('ldap', ldap_plugin)

        provideAdapter(FakeLDAPSearchUtility)

    def test_imports_users(self):
        FAKE_LDAP_USERFOLDER.users = [
            create(Builder('ldapuser').named('sk1m1')),
            create(Builder('ldapuser').named('john'))]

        updater = IOGDSUpdater(self.portal)

        updater.import_users()
        self.assertIsNotNone(ogds_service().fetch_user('sk1m1'))
        self.assertIsNotNone(ogds_service().fetch_user('john'))

    def test_flags_users_not_present_in_ldap_as_inactive(self):
        create(Builder('ogds_user').id('john.doe'))
        create(Builder('ogds_user').id('hugo.boss'))

        FAKE_LDAP_USERFOLDER.users = [
            create(Builder('ldapuser').named('hugo.boss')),
            create(Builder('ldapuser').named('new.user'))]

        updater = IOGDSUpdater(self.portal)

        updater.import_users()
        self.assertFalse(ogds_service().fetch_user('john.doe').active)
        self.assertTrue(ogds_service().fetch_user('hugo.boss').active)
        self.assertTrue(ogds_service().fetch_user('new.user').active)

    def test_imports_groups(self):
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup').named('og_mandant1_users'))]

        updater = IOGDSUpdater(self.portal)

        updater.import_groups()
        self.assertIsNotNone(ogds_service().fetch_group('og_mandant1_users'))

    def test_imports_group_memberships(self):
        sk1m1 = create(Builder('ldapuser').named('sk1m1'))
        sk2m1 = create(Builder('ldapuser').named('sk2m1'))
        sk1m2 = create(Builder('ldapuser').named('sk1m2'))
        sk2m2 = create(Builder('ldapuser').named('sk2m2'))

        FAKE_LDAP_USERFOLDER.users = [sk1m1, sk2m1, sk1m2, sk2m2]
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup')
                   .named('og_mandant1_users')
                   .with_members([sk1m1, sk2m1])),
            create(Builder('ldapgroup')
                   .named('og_mandant2_users')
                   .with_members([sk1m2, sk2m2])),
        ]

        updater = IOGDSUpdater(self.portal)

        updater.import_users()
        updater.import_groups()

        ogds = ogds_service()
        og_mandant1_users = ogds.fetch_group('og_mandant1_users')
        og_mandant2_users = ogds.fetch_group('og_mandant2_users')

        self.assertItemsEqual(
            [ogds.fetch_user('sk1m1'), ogds.fetch_user('sk2m1')],
            og_mandant1_users.users)
        self.assertItemsEqual(
            [ogds.fetch_user('sk1m2'), ogds.fetch_user('sk2m2')],
            og_mandant2_users.users)

    def test_imports_handle_unicode_values_properly(self):
        klaus = create(Builder('ldapuser')
                       .named('klaus.r\xc3\xbcegg')
                       .having(firstname='Klaus',
                               lastname='R\xc3\xbcegg',
                               l=['M\xc3\xbcnsingen'],
                               o=['M\xc3\xbcller & Co'],
                               ou=['M\xc3\xbcnster'],
                               street=['F\xc3\xa4hrstrasse 13']))

        group = create(Builder('ldapgroup')
                       .named('f\xc3\xbchrung')
                       .with_members([klaus]))

        FAKE_LDAP_USERFOLDER.users = [klaus]
        FAKE_LDAP_USERFOLDER.groups = [group]

        updater = IOGDSUpdater(self.portal)

        updater.import_users()
        updater.import_groups()

        ogds_user = ogds_service().fetch_user(u'klaus.r\xfcegg')
        self.assertEquals(u'klaus.r\xfcegg', ogds_user.userid)
        self.assertEquals(u'Klaus', ogds_user.firstname)
        self.assertEquals(u'R\xfcegg', ogds_user.lastname)
        self.assertEquals(u'klaus.r\xfcegg@4teamwork.ch', ogds_user.email)

        ogds_group = ogds_service().fetch_group(u'f\xfchrung')
        self.assertEquals(u'f\xfchrung', ogds_group.groupid)
