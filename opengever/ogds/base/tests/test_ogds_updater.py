# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing.freezer import freeze
from opengever.base.model import create_session
from opengever.ogds.base.interfaces import IOGDSSyncConfiguration
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.sync.import_stamp import get_ogds_sync_stamp
from opengever.ogds.base.sync.import_stamp import ogds_sync_within_24h
from opengever.ogds.base.sync.import_stamp import update_sync_stamp
from opengever.ogds.base.sync.ogds_updater import CaseInsensitiveDict
from opengever.ogds.base.tests.ldaphelpers import FakeLDAPPlugin
from opengever.ogds.base.tests.ldaphelpers import FakeLDAPSearchUtility
from opengever.ogds.base.tests.ldaphelpers import FakeLDAPUserFolder
from opengever.ogds.models.group import Group
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from unittest import TestCase
import transaction


FAKE_LDAP_USERFOLDER = FakeLDAPUserFolder()
BLACKLISTED_USER_COLUMNS = {
    'absent',
    'absent_from',
    'absent_to',
    'last_login',
}
BLACKLISTED_GROUP_COLUMNS = {'is_local'}


class TestOGDSUpdater(FunctionalTestCase):

    def setUp(self):
        super(TestOGDSUpdater, self).setUp()
        self.portal = self.layer['portal']

        ldap_plugin = FakeLDAPPlugin(FAKE_LDAP_USERFOLDER)
        self.portal.acl_users._setObject('ldap', ldap_plugin)

        self.portal.getSiteManager().registerAdapter(FakeLDAPSearchUtility)

    def test_imports_users(self):
        FAKE_LDAP_USERFOLDER.users = [
            create(Builder('ldapuser').named('sk1m1')),
            create(Builder('ldapuser').named('john'))]

        updater = IOGDSUpdater(self.portal)

        updater.import_users()
        self.assertIsNotNone(ogds_service().fetch_user('sk1m1'))
        self.assertIsNotNone(ogds_service().fetch_user('john'))

    def test_skips_duplicates_users_with_capitalization(self):
        create(Builder('ogds_user')
               .id('peter')
               .having(firstname=u'Hans', lastname=u'Peter'))

        FAKE_LDAP_USERFOLDER.users = [
            create(Builder('ldapuser').named('PETER'))]

        updater = IOGDSUpdater(self.portal)
        updater.import_users()

        self.assertEqual([TEST_USER_ID, 'peter'],
                         [user.userid for user in ogds_service().all_users()])

    def test_handles_group_membership_update_when_userid_case_changes(self):
        old_group = create(Builder('ogds_group')
                           .having(groupid='old_group'))

        create(Builder('ogds_user')
               .id('peter')
               .in_group(old_group)
               .having(firstname=u'Hans',
                       lastname=u'Peter'))

        # LDAP user with different case than existing OGDS user
        peter = create(Builder('ldapuser').named('PETER'))
        FAKE_LDAP_USERFOLDER.users = [peter]

        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup')
                   .named('new_group')
                   .with_members([peter]))
        ]

        updater = IOGDSUpdater(self.portal)
        updater.import_groups()

        ogds_user = ogds_service().fetch_user('peter')
        self.assertEqual([u'new_group'], [g.groupid for g in ogds_user.groups])

    def test_properties_update_when_userid_case_changes(self):
        existing_user = create(Builder('ogds_user')
                               .id('someuserid')
                               .having(email='old@example.org'))

        peter = create(Builder('ldapuser')
                       .named('SOMEUSERID')
                       .having(firstname='Peter',
                               lastname='Muster',
                               email='peter@new.example.org'))
        FAKE_LDAP_USERFOLDER.users = [peter]

        updater = IOGDSUpdater(self.portal)
        updater.import_users()

        create_session().expunge(existing_user)
        updated_user = ogds_service().fetch_user('someuserid')
        self.assertEqual('peter@new.example.org', updated_user.email)
        self.assertEqual([TEST_USER_ID, 'someuserid'],
                         [user.userid for user in ogds_service().all_users()])

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

    def test_mismapped_user_columns(self):
        all_column_names = {column.name for column in User.__table__.columns}

        self.assertEqual(set(),
                         User.column_names_to_sync.intersection(BLACKLISTED_USER_COLUMNS),
                         'Column found in both lists. The column should either be in the '
                         'column_names_to_sync list of the user model if it needs syncing with the '
                         'LDAP, or in the BLACKLISTED_USER_COLUMNS list here.')

        self.assertEqual(set(),
                         all_column_names.difference(
                            User.column_names_to_sync.union(BLACKLISTED_USER_COLUMNS)),
                         'A new column was added to the User model, it should either be added to '
                         'the column_names_to_sync list of the user model if it needs syncing with '
                         'the LDAP, or in the BLACKLISTED_USER_COLUMNS list here.')

        self.assertEqual(set(),
                         User.column_names_to_sync.union(BLACKLISTED_USER_COLUMNS).difference(
                            all_column_names),
                         'A column was deleted from the user model, but is still either in the '
                         'column_names_to_sync list of the user model or in the '
                         'BLACKLISTED_USER_COLUMNS list here')

    def test_imports_groups(self):
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup').named('og_mandant1_users'))]

        updater = IOGDSUpdater(self.portal)

        updater.import_groups()
        self.assertIsNotNone(ogds_service().fetch_group('og_mandant1_users'))

    def test_skips_groups_with_non_ascii_characters(self):
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup').named('og_mandänt_users'))]

        updater = IOGDSUpdater(self.portal)

        updater.import_groups()
        self.assertIsNone(ogds_service().fetch_group(u'og_mandänt_users'))

    def test_mismapped_group_columns(self):
        all_column_names = {column.name for column in Group.__table__.columns}

        self.assertEqual(set(),
                         Group.column_names_to_sync.intersection(BLACKLISTED_GROUP_COLUMNS),
                         'Column found in both lists. The column should either be in the '
                         'column_names_to_sync list of the group model if it needs syncing with the'
                         ' LDAP, or in the BLACKLISTED_USER_COLUMNS list here.')

        self.assertEqual(set(),
                         all_column_names.difference(
                            Group.column_names_to_sync.union(BLACKLISTED_GROUP_COLUMNS)),
                         'A new column was added to the group model, it should either be added to '
                         'the column_names_to_sync list of the group model if it needs syncing with'
                         ' the LDAP, or in the BLACKLISTED_GROUP_COLUMNS list here.')

        self.assertEqual(set(),
                         Group.column_names_to_sync.union(BLACKLISTED_GROUP_COLUMNS).difference(
                            all_column_names),
                         'A column was deleted from the group model, but is still either in the '
                         'column_names_to_sync list of the group model or in the '
                         'BLACKLISTED_GROUP_COLUMNS list here')

    def test_uses_title_attribute_for_group_title_when_set(self):
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup')
                   .having(description=u'OG Mandant1 users')
                   .named('og_mandant1_users'))]

        updater = IOGDSUpdater(self.portal)
        updater.import_groups()
        group = ogds_service().fetch_group('og_mandant1_users')
        self.assertIsNone(group.title)

        api.portal.set_registry_record(name='group_title_ldap_attribute',
                                       value=u'description',
                                       interface=IOGDSSyncConfiguration)
        updater = IOGDSUpdater(self.portal)
        updater.import_groups()

        group = ogds_service().fetch_group('og_mandant1_users')
        # Bulk updates are not session aware, thus we need to refresh
        ogds_service().session.refresh(group)
        self.assertEquals(u'OG Mandant1 users', group.title)

    def test_handles_multivalues_group_titles(self):
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup')
                   .having(description=[u'OG Mandant1 users', u'\xc4ddition'])
                   .named('og_mandant1_users'))]

        updater = IOGDSUpdater(self.portal)
        updater.import_groups()
        group = ogds_service().fetch_group('og_mandant1_users')
        self.assertIsNone(group.title)

        api.portal.set_registry_record(name='group_title_ldap_attribute',
                                       value=u'description',
                                       interface=IOGDSSyncConfiguration)
        updater = IOGDSUpdater(self.portal)
        updater.import_groups()

        group = ogds_service().fetch_group('og_mandant1_users')
        # Bulk updates are not session aware, thus we need to refresh
        ogds_service().session.refresh(group)
        self.assertEquals(u'OG Mandant1 users \xc4ddition', group.title)

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

    def test_removes_memberships_when_deactivating_groups(self):
        user1 = create(Builder('ldapuser').named('user1'))
        user2 = create(Builder('ldapuser').named('user2'))

        FAKE_LDAP_USERFOLDER.users = [user1, user2]
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup')
                   .named('group1')
                   .with_members([user1, user2])),
        ]

        updater = IOGDSUpdater(self.portal)

        updater.import_users()
        updater.import_groups()

        ogds = ogds_service()
        group1 = ogds.fetch_group('group1')
        self.assertTrue(group1.active)
        self.assertEqual(['user1', 'user2'], [user.userid for user in group1.users])

        FAKE_LDAP_USERFOLDER.groups = []
        updater.import_groups()
        transaction.commit()
        self.assertFalse(group1.active)
        self.assertEqual([], group1.users)

    def test_user_import_handles_unicode_values_properly(self):
        klaus = create(Builder('ldapuser')
                       .named('klaus.r\xc3\xbcegg')
                       .having(firstname='Klaus',
                               lastname='R\xc3\xbcegg',
                               l=['M\xc3\xbcnsingen'],  # noqa
                               o=['M\xc3\xbcller & Co'],  # noqa
                               title=['Gesch\xc3\xa4ftsf\xc3\xbchrer'],  # noqa
                               ou=['M\xc3\xbcnster'],  # noqa
                               street=['F\xc3\xa4hrstrasse 13']))

        FAKE_LDAP_USERFOLDER.users = [klaus]
        updater = IOGDSUpdater(self.portal)
        updater.import_users()

        ogds_user = ogds_service().fetch_user(u'klaus.r\xfcegg')
        self.assertEqual(u'klaus.r\xfcegg', ogds_user.userid)
        self.assertEqual(u'Klaus', ogds_user.firstname)
        self.assertEqual(u'R\xfcegg', ogds_user.lastname)
        self.assertEqual(u'klaus.r\xfcegg@example.com', ogds_user.email)
        self.assertEqual(u'Gesch\xe4ftsf\xfchrer', ogds_user.title)

    def test_does_not_overwrite_local_groups(self):
        groupid = u'local.group'
        ogds_group = create(Builder('ogds_group').id(groupid))
        ogds_user = create(Builder('ogds_user').id('john.doe'))
        ogds_group.users.append(ogds_user)

        ldap_user = create(Builder('ldapuser').named('sk1m1'))
        FAKE_LDAP_USERFOLDER.users = [ldap_user]
        FAKE_LDAP_USERFOLDER.groups = [create(
            Builder('ldapgroup').named(groupid).with_members([ldap_user]))]
        updater = IOGDSUpdater(self.portal)
        updater.import_users()

        ogds_group.is_local = True
        updater.import_groups()
        self.assertItemsEqual([user.userid for user in ogds_group.users],
                              [ogds_user.userid])

        ogds_group.is_local = False
        updater.import_groups()
        self.assertItemsEqual([user.userid for user in ogds_group.users],
                              [ldap_user[1]['userid']])

    def test_imports_local_groups(self):
        create(Builder('group').with_groupid('my_local_group'))

        updater = IOGDSUpdater(self.portal)
        updater.import_local_groups()

        group = ogds_service().fetch_group('my_local_group')
        self.assertEqual(group.title, 'my_local_group')

    def test_import_local_groups_can_handle_non_ascii_characters_in_title(self):
        self.portal.portal_groups.addGroup('a_local_group', title=u'H\u79d2')
        updater = IOGDSUpdater(self.portal)
        updater.import_local_groups()

        group = ogds_service().fetch_group('a_local_group')
        self.assertEqual(group.title, u'H\u79d2')

    def test_deactivates_local_groups(self):
        create(Builder('ogds_group')
               .id('my_local_group').having(is_local=True, active=True))

        updater = IOGDSUpdater(self.portal)
        updater.import_local_groups()

        group = ogds_service().fetch_group('my_local_group')
        self.assertEqual(group.active, False)

    def test_adds_members_to_local_groups(self):
        user = api.user.get(username='test_user_1_')
        create(Builder('group')
               .with_groupid('my_local_group')
               .with_members(user))

        updater = IOGDSUpdater(self.portal)
        updater.import_local_groups()

        group = ogds_service().fetch_group('my_local_group')
        self.assertEqual([u.userid for u in group.users], ['test_user_1_'])

    def test_removes_members_from_local_groups(self):
        ogds_group = create(Builder('ogds_group')
                            .id('my_local_group')
                            .having(is_local=True, active=True))
        ogds_user = create(Builder('ogds_user').id('john.doe'))
        ogds_group.users.append(ogds_user)

        create(Builder('group')
               .with_groupid('my_local_group'))

        updater = IOGDSUpdater(self.portal)
        updater.import_local_groups()

        self.assertNotIn('john.doe', ogds_group.users)

    def test_import_ignores_duplicate_group_if_global_group_exists(self):
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup').named('duplicate_group'))
        ]
        create(Builder('group').with_groupid('duplicate_group'))

        updater = IOGDSUpdater(self.portal)

        updater.import_groups()
        updater.import_local_groups()

        group = ogds_service().fetch_group('duplicate_group')
        self.assertEqual(group.is_local, False)

    def test_import_ignores_duplicate_group_if_local_group_exists(self):
        FAKE_LDAP_USERFOLDER.groups = [
            create(Builder('ldapgroup').named('duplicate_group'))
        ]
        create(Builder('group').with_groupid('duplicate_group'))

        updater = IOGDSUpdater(self.portal)

        updater.import_local_groups()
        updater.import_groups()

        group = ogds_service().fetch_group('duplicate_group')
        self.assertEqual(group.is_local, True)


class TestImportStamp(IntegrationTestCase):

    def test_get_ogds_sync_stamp(self):
        self.assertIsNone(get_ogds_sync_stamp())

        with freeze(datetime(2021, 9, 11, 12, 45)):
            update_sync_stamp(self.portal)

        self.assertEqual(datetime(2021, 9, 11, 12, 45), get_ogds_sync_stamp())

    def test_ogds_sync_within_24h_helper(self):
        self.assertIsNone(get_ogds_sync_stamp())
        self.assertFalse(ogds_sync_within_24h())

        with freeze((datetime.now() - timedelta(hours=23))):
            update_sync_stamp(self.portal)
        self.assertTrue(ogds_sync_within_24h())

        with freeze((datetime.now() - timedelta(hours=25))):
            update_sync_stamp(self.portal)
        self.assertFalse(ogds_sync_within_24h())


class TestCaseInsensitiveDict(TestCase):

    def setUp(self):
        self.dct = CaseInsensitiveDict({
            'foo': 42,
            'FooBar': 1,
            'qux': 'lowercase',
            'QUX': 'uppercase',
        })

    def test_original_case_is_preserved_for_keys(self):
        self.assertItemsEqual(
            ['foo', 'FooBar', 'qux', 'QUX'], self.dct.keys())

    def test_contains_is_case_insensitive(self):
        self.assertIn('FOO', self.dct)
        self.assertIn('foo', self.dct)

    def test_get_is_case_insensitive(self):
        self.assertEqual(42, self.dct.get('FOO'))

    def test_getitem_is_case_insensitive(self):
        self.assertEqual(42, self.dct['FOO'])

    def test_get_picks_exact_case_match_first(self):
        self.assertEqual('lowercase', self.dct.get('qux'))
        self.assertEqual('uppercase', self.dct.get('QUX'))

    def test_getitem_picks_exact_case_match_first(self):
        self.assertEqual('lowercase', self.dct['qux'])
        self.assertEqual('uppercase', self.dct['QUX'])
