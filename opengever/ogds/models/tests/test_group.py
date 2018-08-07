from ftw.builder import Builder
from ftw.builder import create
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
        g1 = Group('group-one')
        self.session.add(g1)
        self.commit()

        groups = self.session.query(Group).all()
        self.assertEquals(len(groups), 1)

        g1 = groups[0]
        self.assertEquals(g1.groupid, 'group-one')

    def test_repr(self):
        self.assertEquals(str(Group('a-group')),
                          '<Group a-group>')

    def test_create_sets_attrs(self):
        attrs = {
            'groupid': 'admins',
            'title': 'Administrators',
            }

        g2 = Group(**attrs)

        for key, value in attrs.items():
            self.assertEquals(getattr(g2, key), value)

    def test_users_in_group(self):
        john = create(Builder('ogds_user').id('john.doe'))
        users = create(Builder('ogds_group').id('users'))
        aaaa = create(Builder('ogds_group').id('aaaa'))
        self.commit()

        self.assertNotIn(john, users.users)
        users.users.append(john)
        aaaa.users.append(john)
        self.assertIn(john, users.users)

        self.assertIn(john, users.users)
        self.assertEqual([u'aaaa', u'users'], [group.groupid for group in john.groups])

        # remove john from users
        users.users.remove(john)
        self.assertNotIn(john, users.users)

        self.assertNotIn(john, users.users)
