from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.tests.base import OGDSTestCase


class TestOrgUnit(OGDSTestCase):
    def test_create_org_unit_id_required(self):
        with self.assertRaises(TypeError):
            OrgUnit()

    def test_creatable(self):
        org_units = self.session.query(OrgUnit).all()
        self.assertEqual(len(org_units), 4)
        self.assertEqual(org_units[-1].unit_id, 'unitd')

    def test_repr(self):
        self.assertEqual(str(OrgUnit('a-unit')), '<OrgUnit a-unit>')

    def test_create_sets_attrs(self):
        attrs = {'unit_id': 'unit-two', 'title': 'Unit two', 'enabled': False}
        org_unit = OrgUnit(**attrs)
        for key, value in attrs.items():
            self.assertEqual(getattr(org_unit, key), value)

    def test_representation_returns_OrgUnit_and_id(self):
        self.assertEqual('<OrgUnit unita>', repr(self.org_unit_a))

    def test_equality(self):
        self.assertEqual(OrgUnit('aa'), OrgUnit('aa'))
        self.assertNotEqual(OrgUnit('aa'), OrgUnit('bb'))
        self.assertNotEqual(OrgUnit('aa'), OrgUnit(123))
        self.assertNotEqual(OrgUnit('aa'), OrgUnit(None))
        self.assertNotEqual(OrgUnit('aa'), object())
        self.assertNotEqual(OrgUnit('aa'), None)

    def test_label_returns_unit_title(self):
        self.assertEqual('Unit A', self.org_unit_a.label())

    def test_id_returns_unit_id(self):
        self.assertEqual('unita', self.org_unit_a.id())

    def test_assigned_users_returns_all_users_from_the_units_usersgroup(self):
        self.assertItemsEqual([self.john, self.hugo], self.org_unit_a.assigned_users())

    def test_inbox_returns_inbox_according_to_the_org_unit(self):
        inbox = self.org_unit_a.inbox()
        self.assertEqual('inbox:unita', inbox.id())
        self.assertEqual(self.org_unit_a, inbox._org_unit)

    def test_label_is_not_prefixed_for_lone_org_unit(self):
        self.session.delete(self.org_unit_b)
        self.session.delete(self.org_unit_c)
        self.session.delete(self.org_unit_d)
        org_unit = self.service.fetch_org_unit('unita')
        self.assertEqual(u'a label', org_unit.prefix_label(u'a label'))

    def test_label_is_prefixed_for_multiple_org_unit(self):
        org_unit = self.service.fetch_org_unit('unita')
        self.assertEqual(u'Unit A / a label', org_unit.prefix_label(u'a label'))

    def test_inboxgroup_agency_is_inactive_for_lone_org_unit(self):
        self.session.delete(self.org_unit_b)
        self.session.delete(self.org_unit_c)
        self.session.delete(self.org_unit_d)
        org_unit = self.service.fetch_org_unit('unita')
        self.assertFalse(org_unit.is_inboxgroup_agency_active)

    def test_inboxgroup_agency_is_active_for_multiple_org_units(self):
        org_unit = self.service.fetch_org_unit('unita')
        self.assertTrue(org_unit.is_inboxgroup_agency_active)


class TestUnitGroups(OGDSTestCase):
    def test_users_in_members_group(self):
        self.assertItemsEqual([self.john, self.hugo], self.org_unit_a.users_group.users)

    def test_users_in_inbox_group(self):
        self.assertItemsEqual([self.john, self.peter], self.org_unit_a.inbox_group.users)

    def test_assigned_users_returns_all_users_from_the_usersgroup(self):
        self.assertItemsEqual([self.john, self.hugo], self.org_unit_a.assigned_users())
