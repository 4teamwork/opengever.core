from opengever.ogds.models.exceptions import RecordNotFound
from opengever.ogds.models.tests.base import OGDSTestCase


class TestOGDSServiceUserMehtods(OGDSTestCase):

    def test_fetch_user_by_id(self):
        self.assertEqual(self.john, self.service.fetch_user('john'))

    def test_fetch_user_returns_none_when_no_user_found(self):
        self.assertEqual(None, self.service.fetch_user('foobar'))

    def test_find_user_user_by_id(self):
        self.assertEqual(self.john, self.service.find_user('john'))

    def test_find_user_raise_when_no_user_found(self):
        with self.assertRaises(RecordNotFound) as cm:
            self.service.find_user('foobar')

        self.assertEqual('no User found for foobar', str(cm.exception))

    def test_all_users_returns_a_list_of_every_user(self):
        self.assertItemsEqual([self.john, self.hugo, self.peter, self.jack, self.bob, self.admin], self.service.all_users())

    def test_all_users_returns_empty_list_when_no_user_exists(self):
        self.session.delete(self.john)
        self.session.delete(self.hugo)
        self.session.delete(self.peter)
        self.session.delete(self.jack)
        self.session.delete(self.bob)
        self.session.delete(self.admin)
        self.assertEqual([], self.service.all_users())

    def test_inactive_users_filters_by_active_false(self):
        self.assertItemsEqual([self.bob, self.admin], self.service.inactive_users())

    def test_filter_users(self):
        self.assertEqual([self.john, self.jack], self.service.filter_users(['smith']).all())


class TestOGDSServiceGroupMethods(OGDSTestCase):

    def test_fetch_group_by_id(self):
        self.assertEqual(self.members_a, self.service.fetch_group('members_a'))

    def test_all_groups_returns_active_groups_only_by_default(self):
        expected_groups = [self.members_a, self.members_b, self.members_c, self.inbox_members]
        self.assertItemsEqual(expected_groups, self.service.all_groups())

    def test_all_groups_includes_inactive_groups_when_active_flag_is_false(self):
        expected_groups = [self.members_a, self.members_b, self.members_c, self.inbox_members, self.inactive_members]
        self.assertItemsEqual(expected_groups, self.service.all_groups(active_only=False))

    def test_assigned_groups_returns_empty_list_if_no_groups_are_assigned(self):
        self.assertEqual([], self.service.assigned_groups('bob'))

    def test_assigned_groups_returns_a_list_of_multiple_groups(self):
        groups = self.service.assigned_groups('john')
        self.assertSequenceEqual([self.members_a, self.inbox_members], groups)


class TestOGDSServiceAdminUnitMethods(OGDSTestCase):

    def test_has_multiple_admin_units(self):
        self.assertTrue(self.service.has_multiple_admin_units())

    def test_has_multiple_admin_units_counts_only_enabled_admin_units(self):
        self.admin_unit_1.enabled = False
        self.admin_unit_2.enabled = False
        self.assertFalse(self.service.has_multiple_admin_units())

    def test_fetch_admin_unit_by_unit_id(self):
        self.assertEqual(self.admin_unit_1, self.service.fetch_admin_unit('canton_1'))

    def test_fetching_disabled_admin_unit_by_unit_id(self):
        self.assertEqual(self.admin_unit_3, self.service.fetch_admin_unit('canton_3'))

    def test_fetch_not_existing_admin_unit_returns_none(self):
        self.assertIsNone(self.service.fetch_admin_unit('admin_xx'))

    def test_all_admin_units_returns_a_list_of_all_enabled_admin_units(self):
        self.assertSequenceEqual([self.admin_unit_1, self.admin_unit_2], self.service.all_admin_units())

    def test_all_admin_units_includes_disabled_orgunits_when_flag_is_set(self):
        expected_admin_units = [self.admin_unit_1, self.admin_unit_2, self.admin_unit_3]
        self.assertSequenceEqual(expected_admin_units, self.service.all_admin_units(enabled_only=False))


class TestOGDSServiceOrgUnitMethods(OGDSTestCase):

    def test_has_multiple_org_units(self):
        self.assertTrue(self.service.has_multiple_org_units())

    def test_falsy_multiple_org_units(self):
        self.session.delete(self.org_unit_b)
        self.session.delete(self.org_unit_c)
        self.session.delete(self.org_unit_d)
        self.assertFalse(self.service.has_multiple_org_units())

    def test_fetch_org_unit_by_unit_id(self):
        self.assertEqual(self.org_unit_c, self.service.fetch_org_unit('unitc'))

    def test_fetch_org_unit_returns_none_when_no_org_unit_is_found(self):
        self.assertIsNone(self.service.fetch_org_unit('not-existing-unit'))

    def test_assigned_org_units_returns_a_list_of_orgunit(self):
        units = self.service.assigned_org_units('hugo')
        self.assertSequenceEqual([self.org_unit_a, self.org_unit_b], units)

    def test_all_org_units_returns_list_of_all_orgunits(self):
        units = self.service.all_org_units()
        self.assertSequenceEqual([self.org_unit_a, self.org_unit_b, self.org_unit_c], units)

    def test_all_org_units_includes_disabled_orgunits_when_flag_is_set(self):
        units = self.service.all_org_units(enabled_only=False)
        self.assertSequenceEqual([self.org_unit_a, self.org_unit_b, self.org_unit_c, self.org_unit_d], units)
