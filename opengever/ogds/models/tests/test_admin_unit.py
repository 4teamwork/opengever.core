from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.tests.base import OGDSTestCase


class TestAdminUnit(OGDSTestCase):

    def setUp(self):
        super(TestAdminUnit, self).setUp()
        self.john = create(Builder('ogds_user').id('john'))
        self.hugo = create(Builder('ogds_user').id('hugo'))
        self.peter = create(Builder('ogds_user').id('peter'))
        self.jack = create(Builder('ogds_user').id('jack'))

        self.members_a = create(Builder('ogds_group')
                                .id('members_a')
                                .having(users=[self.john, self.hugo]))

        self.members_b = create(Builder('ogds_group')
                                .id('members_b')
                                .having(users=[self.peter, self.hugo]))

        self.members_c = create(Builder('ogds_group')
                                .id('members_c')
                                .having(users=[self.jack]))

        self.org_unit_a = create(Builder('org_unit')
                                 .id('unita')
                                 .having(title='Unit A',
                                         users_group=self.members_a,
                                         admin_unit_id='canton'))

        self.org_unit_b = create(Builder('org_unit')
                                 .id('unitb')
                                 .having(title='Unit B',
                                         users_group=self.members_b,
                                         admin_unit_id='canton'))

        self.org_unit_c = create(Builder('org_unit')
                                 .id('unitc')
                                 .having(title='Unit C',
                                         users_group=self.members_c,
                                         admin_unit_id='other'))

        self.admin_unit = create(Builder('admin_unit')
                                 .id('canton')
                                 .having(title='Canton Unit')
                                 .assign_org_units([self.org_unit_a,
                                                   self.org_unit_b]))
        self.commit()

    def test_equality(self):
        self.assertEqual(AdminUnit('aa'), AdminUnit('aa'))
        self.assertNotEqual(AdminUnit('aa'), AdminUnit('bb'))
        self.assertNotEqual(AdminUnit('aa'), AdminUnit(123))
        self.assertNotEqual(AdminUnit('aa'), AdminUnit(None))
        self.assertNotEqual(AdminUnit('aa'), object())
        self.assertNotEqual(AdminUnit('aa'), None)

    def test_representation_returns_OrgUnit_and_id(self):
        self.assertEquals('<AdminUnit canton>', repr(self.admin_unit))

    def test_label_returns_unit_title(self):
        self.assertEquals('Canton Unit', self.admin_unit.label())

    def test_label_returns_emtpy_string_when_title_is_none(self):
        self.admin_unit.title = None
        self.assertEquals('', self.admin_unit.label())

    def test_id_returns_unit_id(self):
        self.assertEquals('canton', self.admin_unit.id())

    def test_org_units_getter_returns_correct_orgunits(self):
        self.assertSequenceEqual([self.org_unit_a, self.org_unit_b],
                                 self.admin_unit.org_units)

    def test_assigned_users_return_assigned_users_of_all_orgunits(self):
        self.assertItemsEqual([self.hugo, self.peter, self.john],
                              self.admin_unit.assigned_users())

    def test_is_user_assigned_to_admin_unit_returns_true(self):
        self.assertTrue(self.admin_unit.is_user_assigned(self.john))

    def test_is_user_assigned_to_admin_unit_returns_false(self):
        self.assertFalse(self.admin_unit.is_user_assigned(self.jack))

    def test_is_user_assigned_handles_missing_ogds_user(self):
        self.assertFalse(self.admin_unit.is_user_assigned(None))

    def test_prefix_label(self):
        self.assertEqual(u'Canton Unit / foo',
                         self.admin_unit.prefix_label('foo'))
