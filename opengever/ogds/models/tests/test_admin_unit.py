from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.tests.base import OGDSTestCase


class TestAdminUnit(OGDSTestCase):
    def test_equality(self):
        self.assertEqual(AdminUnit('aa'), AdminUnit('aa'))
        self.assertNotEqual(AdminUnit('aa'), AdminUnit('bb'))
        self.assertNotEqual(AdminUnit('aa'), AdminUnit(123))
        self.assertNotEqual(AdminUnit('aa'), AdminUnit(None))
        self.assertNotEqual(AdminUnit('aa'), object())
        self.assertNotEqual(AdminUnit('aa'), None)

    def test_representation_returns_OrgUnit_and_id(self):
        self.assertEqual('<AdminUnit canton_1>', repr(self.admin_unit_1))

    def test_label_returns_unit_title(self):
        self.assertEqual('Canton 1 Unit', self.admin_unit_1.label())

    def test_label_returns_emtpy_string_when_title_is_none(self):
        self.admin_unit_1.title = None
        self.assertEqual('', self.admin_unit_1.label())

    def test_id_returns_unit_id(self):
        self.assertEqual('canton_1', self.admin_unit_1.id())

    def test_org_units_getter_returns_correct_orgunits(self):
        self.assertSequenceEqual([self.org_unit_a, self.org_unit_b], self.admin_unit_1.org_units)

    def test_assigned_users_return_assigned_users_of_all_orgunits(self):
        self.assertItemsEqual([self.hugo, self.peter, self.john], self.admin_unit_1.assigned_users())

    def test_is_user_assigned_to_admin_unit_returns_true(self):
        self.assertTrue(self.admin_unit_1.is_user_assigned(self.john))

    def test_is_user_assigned_to_admin_unit_returns_false(self):
        self.assertFalse(self.admin_unit_1.is_user_assigned(self.jack))

    def test_is_user_assigned_handles_missing_ogds_user(self):
        self.assertFalse(self.admin_unit_1.is_user_assigned(None))

    def test_prefix_label(self):
        self.assertEqual(u'Canton 1 Unit / foo', self.admin_unit_1.prefix_label('foo'))
