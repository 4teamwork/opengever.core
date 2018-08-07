from opengever.ogds.models.tests.base import OGDSTestCase
from opengever.ogds.models.user import User
from ftw.builder import Builder
from ftw.builder import create


class TestUserModel(OGDSTestCase):

    def test_create_userid_required(self):
        with self.assertRaises(TypeError):
            User()

    def test_equality(self):
        self.assertEqual(User('aa'), User('aa'))
        self.assertNotEqual(User('aa'), User('bb'))
        self.assertNotEqual(User('aa'), User(123))
        self.assertNotEqual(User('aa'), User(None))
        self.assertNotEqual(User('aa'), object())
        self.assertNotEqual(User('aa'), None)

    def test_creatable(self):
        create(Builder("ogds_user").id('user-one'))
        self.commit()

        users = self.session.query(User).all()
        self.assertEquals(len(users), 1)

        u1 = users[0]
        self.assertEquals(u1.userid, 'user-one')

    def test_repr(self):
        self.assertEquals(str(User('a-user')),
                          '<User a-user>')

    def test_fullname_is_first_and_lastname(self):
        billy = User("billyj", firstname="billy", lastname="johnson")
        self.assertEquals('johnson billy', billy.fullname())

    def test_fullname_is_only_first_or_lastname_if_other_is_missing(self):
        billy = User("billyj", firstname="billy")
        self.assertEquals('billy', billy.fullname())

        johnson = User("billyj", lastname="johnson")
        self.assertEquals('johnson', johnson.fullname())

    def test_fullname_is_userid_if_no_name_given(self):
        billyj = User("billyj")
        self.assertEquals('billyj', billyj.fullname())

    def test_label_is_the_fullname_with_userid_in_braces(self):
        sammy = User("sammy", firstname="Samuel", lastname="Jackson")
        self.assertEquals("Jackson Samuel (sammy)", sammy.label())

    def test_create_sets_attrs(self):
        attrs = {
            'userid': 'hugo.boss',
            'active': True,
            'firstname': 'Hugo',
            'lastname': 'Boss',

            'directorate_abbr': 'FD',
            'directorate': 'Finanzdepartement',
            'department_abbr': 'FV',
            'department': 'Finanzverwaltung',

            'email': 'hugo@boss.ch',
            'email2': 'hugo@boss.com',
            'url': 'http://boss.ch',
            'phone_office': '012 345 67 89',
            'phone_fax': '012 345 67 81',
            'phone_mobile': '079 123 45 67',

            'salutation': 'Herr',
            'description': 'Meister Boss',
            'address1': 'Bossstrasse 1',
            'address2': 'Oberes Bosshaus',
            'zip_code': '1234',
            'city': 'Bossingen',

            'country': 'Schweiz',

            'import_stamp': 'stamp',
            }

        u2 = User(**attrs)

        for key, value in attrs.items():
            self.assertEquals(getattr(u2, key), value)
