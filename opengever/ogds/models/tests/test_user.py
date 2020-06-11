from opengever.ogds.models.tests.base import OGDSTestCase
from opengever.ogds.models.user import User


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
        users = self.session.query(User).all()
        self.assertEqual(len(users), 6)
        self.assertEqual(users[-1].userid, 'admin')

    def test_repr(self):
        self.assertEqual(str(User('a-user')), '<User a-user>')

    def test_fullname_is_last_and_firstname(self):
        self.assertEqual('Smith John', self.john.fullname())

    def test_fullname_is_only_first_or_lastname_if_other_is_missing(self):
        self.assertEqual('Bob', self.bob.fullname())
        self.assertEqual('Smith', self.jack.fullname())

    def test_fullname_is_userid_if_no_name_given(self):
        self.assertEqual('admin', self.admin.fullname())

    def test_label_is_the_fullname_with_userid_in_braces(self):
        sammy = User('sammy', firstname='Samuel', lastname='Jackson')
        self.assertEqual('Jackson Samuel (sammy)', sammy.label())

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
            'email': 'hugo@example.com',
            'email2': 'hugo@example.com',
            'url': 'http://example.com',
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
        }

        user = User(**attrs)

        for key, value in attrs.items():
            self.assertEqual(getattr(user, key), value)
