from opengever.ogds.models.exceptions import RecordNotFound
from opengever.ogds.models.service import OGDSService
from opengever.ogds.models.tests.base import OGDSTestCase
from ftw.builder import Builder
from ftw.builder import create


class TestOGDSService(OGDSTestCase):

    def setUp(self):
        super(TestOGDSService, self).setUp()
        self.service = OGDSService(self.session)

    def test_fetch_user_by_id(self):
        jane = create(Builder('ogds_user').id('jane'))
        self.assertEquals(jane, self.service.fetch_user("jane"))

    def test_fetch_group_by_id(self):
        group = create(Builder('ogds_group').id('group_a'))
        self.assertEquals(group, self.service.fetch_group("group_a"))

    def test_fetch_user_returns_none_when_no_user_found(self):
        self.assertEquals(None, self.service.fetch_user("jane"))

    def test_find_user_user_by_id(self):
        jane = create(Builder('ogds_user').id('jane'))
        self.assertEquals(jane, self.service.find_user("jane"))

    def test_find_user_raise_when_no_user_found(self):
        with self.assertRaises(RecordNotFound) as cm:
            self.service.find_user("jane")

        self.assertEquals("no User found for jane",
                          str(cm.exception))

    def test_all_users_returns_a_list_of_every_user(self):
        create(Builder('admin_unit').assign_org_units([
            create(Builder('org_unit').id('unitc'))
        ]))
        jane = create(Builder('ogds_user').id('jane'))
        peter = create(Builder('ogds_user').id('peter'))

        self.assertItemsEqual([jane, peter], self.service.all_users())

    def test_all_users_returns_empty_list_when_no_user_exists(self):
        self.assertEquals([], self.service.all_users())

    def test_inactive_users_filters_by_active_false(self):
        create(Builder('ogds_user').id('peter').having(active=True))
        jane = create(Builder('ogds_user').id('jane').having(active=False))

        self.assertItemsEqual([jane], self.service.inactive_users())

    def test_filter_users(self):
        jane = create(Builder('ogds_user').id('jane')
                      .having(firstname=u'Jane', lastname=u'Doe'))
        john = create(Builder('ogds_user').id('john')
                      .having(firstname=u'John', lastname=u'doe'))
        peter = create(Builder('ogds_user').id('peter')
                       .having(firstname=u'Peter', lastname=u'Peter'))

        self.assertEqual([jane, john],
                         self.service.filter_users(['doe']).all())


class TestOrgUnitCounters(OGDSTestCase):

    def setUp(self):
        super(TestOrgUnitCounters, self).setUp()
        self.service = OGDSService(self.session)

    def test_has_multiple_org_units(self):
        create(Builder('admin_unit').assign_org_units([
            create(Builder('org_unit').id('unitc')),
            create(Builder('org_unit').id('unita')),
            create(Builder('org_unit').id('unitb')),
            ]))

        self.assertTrue(self.service.has_multiple_org_units())

    def test_falsy_multiple_org_units(self):
        create(Builder('admin_unit').assign_org_units([
            create(Builder('org_unit').id('unitc'))
        ]))

        self.assertFalse(self.service.has_multiple_org_units())


class TestServiceOrgUnitMethods(OGDSTestCase):

    def setUp(self):
        super(TestServiceOrgUnitMethods, self).setUp()
        self.service = OGDSService(self.session)

        self.hugo = create(Builder('ogds_user').id('hugo.boss'))
        self.members = create(Builder('ogds_group')
                              .id('group_a')
                              .having(users=[self.hugo]))
        self.inactive_group = create(Builder('ogds_group')
                                     .id('group_b')
                                     .having(active=False))

        self.admin_unit_1 = create(Builder('admin_unit').id('admin_1')
                                   .having(title='Admin Unit 1'))
        self.admin_unit_2 = create(Builder('admin_unit').id('admin_2')
                                   .having(enabled=False,
                                           title='Admin Unit 2'))
        self.admin_unit_3 = create(Builder('admin_unit').id('admin_3')
                                   .having(title='Admin Unit 3'))

        self.unit_c = create(Builder('org_unit').id('unitc').having(
                             title='Unit C',
                             users_group=self.members,
                             inbox_group=self.members,
                             admin_unit=self.admin_unit_1))
        self.unit_a = create(Builder('org_unit').id('unita').having(
                             title='Unit A',
                             users_group=self.members,
                             inbox_group=self.members,
                             admin_unit=self.admin_unit_1))
        self.unit_b = create(Builder('org_unit').id('unitb').having(
                             title='Unit B',
                             enabled=False,
                             users_group=self.members,
                             inbox_group=self.members,
                             admin_unit=self.admin_unit_1))

        self.commit()

    def test_has_multiple_admin_units(self):
        self.assertTrue(self.service.has_multiple_admin_units())

    def test_has_multiple_admin_units_counts_only_enabled_admin_units(self):
        self.admin_unit_1.enabled = False
        self.admin_unit_2.enabled = False
        self.assertFalse(self.service.has_multiple_admin_units())

    def test_fetch_org_unit_by_unit_id(self):
        unit = self.service.fetch_org_unit('unitc')

        self.assertEquals(self.unit_c, unit)

    def test_fetch_org_unit_returns_none_when_no_org_unit_is_found(self):
        self.assertIsNone(self.service.fetch_org_unit('not-existing-unit'))

    def test_fetch_admin_unit_by_unit_id(self):
        self.assertEquals(self.admin_unit_1,
                          self.service.fetch_admin_unit('admin_1'))

    def test_fetching_disabled_admin_unit_by_unit_id(self):
        self.assertEquals(self.admin_unit_2,
                          self.service.fetch_admin_unit('admin_2'))

    def test_fetch_not_existing_admin_unit_returns_none(self):
        self.assertIsNone(self.service.fetch_admin_unit('admin_xx'))

    def test_assigned_org_units_returns_a_list_of_orgunit(self):
        units = self.service.assigned_org_units('hugo.boss')

        self.assertSequenceEqual([self.unit_a, self.unit_c], units)

    def test_assigned_groups_returns_empty_list_if_no_groups_are_assigned(self):
        create(Builder('ogds_user').id('chuck.norris'))
        groups = self.service.assigned_groups('chuck.norris')

        self.assertEqual([], groups)

    def test_assigned_groups_returns_a_list_of_multiple_groups(self):
        chuck = create(Builder('ogds_user').id('chuck.norris'))

        administrators = create(Builder('ogds_group')
                                .id('administrators')
                                .having(users=[chuck]))

        editors = create(Builder('ogds_group')
                              .id('editors')
                              .having(users=[chuck]))

        groups = self.service.assigned_groups('chuck.norris')

        self.assertSequenceEqual([administrators, editors], groups)

    def test_all_org_units_returns_list_of_all_orgunits(self):
        units = self.service.all_org_units()

        self.assertSequenceEqual([self.unit_a, self.unit_c], units)

    def test_all_org_units_includes_disabled_orgunits_when_flag_is_set(self):
        units = self.service.all_org_units(enabled_only=False)

        self.assertSequenceEqual([self.unit_a, self.unit_b, self.unit_c],
                                 units)

    def test_all_admin_units_returns_a_list_of_all_enabled_admin_units(self):
        self.assertSequenceEqual([self.admin_unit_1, self.admin_unit_3],
                                 self.service.all_admin_units())

    def test_all_admin_units_includes_disabled_orgunits_when_flag_is_set(self):
        self.assertSequenceEqual(
            [self.admin_unit_1, self.admin_unit_2, self.admin_unit_3],
            self.service.all_admin_units(enabled_only=False))

    def test_all_groups_returns_active_groups_only_by_default(self):
        self.assertItemsEqual([self.members], self.service.all_groups())

    def test_all_groups_includes_inactive_groups_when_active_flag_is_false(self):
        self.assertItemsEqual([self.members, self.inactive_group],
                               self.service.all_groups(active_only=False))
