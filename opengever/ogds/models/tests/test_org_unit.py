from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.service import OGDSService
from opengever.ogds.models.tests.base import OGDSTestCase


class TestOrgUnit(OGDSTestCase):

    def setUp(self):
        super(TestOrgUnit, self).setUp()

        self.service = OGDSService(self.session)

        self.john = create(Builder('ogds_user').id('john'))
        self.hugo = create(Builder('ogds_user').id('hugo'))

        self.members = create(Builder('ogds_group')
                              .id('members')
                              .having(users=[self.john, self.hugo]))

        self.org_unit = create(Builder('org_unit')
                               .id('unit')
                               .having(title='Unit A',
                                       users_group=self.members,
                                       inbox_group=self.members))
        self.admin_unit = create(Builder('admin_unit')
                                 .assign_org_units([self.org_unit]))
        self.commit()

    def test_create_org_unit_id_required(self):
        with self.assertRaises(TypeError):
            OrgUnit()

    def test_creatable(self):
        org_units = self.session.query(OrgUnit).all()
        self.assertEquals(len(org_units), 1)

        unit = org_units[0]
        self.assertEquals(unit.unit_id, 'unit')

    def test_repr(self):
        self.assertEquals(str(OrgUnit('a-unit')),
                          '<OrgUnit a-unit>')

    def test_create_sets_attrs(self):
        attrs = {
            'unit_id': 'unit-two',
            'title': 'Unit two',
            'enabled': False,
            }

        c2 = OrgUnit(**attrs)

        for key, value in attrs.items():
            self.assertEquals(getattr(c2, key), value)

    def test_representation_returns_OrgUnit_and_id(self):
        self.assertEquals('<OrgUnit unit>', repr(self.org_unit))

    def test_equality(self):
        self.assertEqual(OrgUnit('aa'), OrgUnit('aa'))
        self.assertNotEqual(OrgUnit('aa'), OrgUnit('bb'))
        self.assertNotEqual(OrgUnit('aa'), OrgUnit(123))
        self.assertNotEqual(OrgUnit('aa'), OrgUnit(None))
        self.assertNotEqual(OrgUnit('aa'), object())
        self.assertNotEqual(OrgUnit('aa'), None)

    def test_label_returns_unit_title(self):
        self.assertEquals(
            'Unit A',
            self.org_unit.label())

    def test_id_returns_unit_id(self):
        self.assertEquals(
            'unit',
            self.org_unit.id())

    def test_assigned_users_returns_all_users_from_the_units_usersgroup(self):
        self.assertItemsEqual([self.john, self.hugo],
                              self.org_unit.assigned_users())

    def test_inbox_returns_inbox_according_to_the_org_unit(self):
        inbox = self.org_unit.inbox()

        self.assertEquals('inbox:unit', inbox.id())
        self.assertEquals(self.org_unit, inbox._org_unit)

    def test_label_is_not_prefixed_for_lone_org_unit(self):
        org_unit = self.service.fetch_org_unit('unit')
        self.assertEqual(u'a label', org_unit.prefix_label(u'a label'))

    def test_label_is_prefixed_for_multiple_org_unit(self):
        create(Builder('org_unit').id('unit-two')
               .having(admin_unit=self.admin_unit))

        org_unit = self.service.fetch_org_unit('unit')
        self.assertEqual(u'Unit A / a label',
                         org_unit.prefix_label(u'a label'))

    def test_inboxgroup_agency_is_inactive_for_lone_org_unit(self):
        org_unit = self.service.fetch_org_unit('unit')

        self.assertFalse(org_unit.is_inboxgroup_agency_active)

    def test_inboxgroup_agency_is_active_for_multiple_org_units(self):
        create(Builder('org_unit').id('unitb')
               .having(admin_unit=self.admin_unit))

        org_unit = self.service.fetch_org_unit('unit')
        self.assertTrue(org_unit.is_inboxgroup_agency_active)


class TestUnitGroups(OGDSTestCase):

    def setUp(self):
        super(TestUnitGroups, self).setUp()
        self.john = create(Builder('ogds_user').id('john'))
        self.hugo = create(Builder('ogds_user').id('hugo'))
        self.peter = create(Builder('ogds_user').id('james'))

        self.inbox = create(Builder('ogds_group')
                            .id('inbox')
                            .having(users=[self.john]))

        self.members = create(Builder('ogds_group')
                              .id('members')
                              .having(users=[self.john, self.hugo]))

        self.unit = create(Builder('org_unit')
                           .id('unit')
                           .having(users_group=self.members,
                                   inbox_group=self.inbox))

        self.admin_unit = create(Builder('admin_unit')
                                 .assign_org_units([self.unit]))

        self.commit()

    def test_users_in_members_group(self):

        self.assertItemsEqual([self.john, self.hugo],
                              self.unit.users_group.users)

    def test_users_in_inbox_group(self):
        self.assertItemsEqual([self.john],
                              self.unit.inbox_group.users)

    def test_assigned_users_returns_all_users_from_the_usersgroup(self):
        self.assertItemsEqual([self.john, self.hugo],
                              self.unit.assigned_users())
