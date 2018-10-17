from opengever.ogds.models.group import Group
from opengever.ogds.models.tests.base import OGDSTestCase


class TestGroupModel(OGDSTestCase):
    def test_create_groupid_required(self):
        with self.assertRaises(TypeError):
            Group()

    def test_equality(self):
        self.assertEqual(Group('aa'), Group('aa'))
        self.assertNotEqual(Group('aa'), Group('bb'))
        self.assertNotEqual(Group('aa'), Group(123))
        self.assertNotEqual(Group('aa'), Group(None))
        self.assertNotEqual(Group('aa'), object())
        self.assertNotEqual(Group('aa'), None)

    def test_creatable(self):
        groups = self.session.query(Group).all()
        self.assertEqual(len(groups), 5)

        g1 = Group('group-one')
        self.session.add(g1)

        groups = self.session.query(Group).all()
        self.assertEqual(len(groups), 6)
        self.assertEqual(groups[-1].groupid, 'group-one')

    def test_repr(self):
        self.assertEqual(str(Group('a-group')), '<Group a-group>')

    def test_create_sets_attrs(self):
        attrs = {'groupid': 'admins', 'title': 'Administrators'}
        group = Group(**attrs)
        for key, value in attrs.items():
            self.assertEqual(getattr(group, key), value)

    def test_users_in_group(self):
        self.assertNotIn(self.john, self.members_b.users)
        self.members_b.users.append(self.john)
        self.assertIn(self.john, self.members_b.users)
        self.assertEqual(['inbox_members', 'members_a', 'members_b'], [group.groupid for group in self.john.groups])

        self.members_b.users.remove(self.john)
        self.assertNotIn(self.john, self.members_b.users)
