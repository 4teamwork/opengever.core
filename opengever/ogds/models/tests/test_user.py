from opengever.base.model import create_session
from opengever.ogds.base.sync.import_stamp import update_sync_stamp
from opengever.ogds.models.tests.base import OGDSTestCase
from opengever.ogds.models.user import User
from opengever.ogds.models.utils import userid_to_username
from opengever.ogds.models.utils import username_to_userid
from opengever.testing import IntegrationTestCase


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
        self.assertEqual(str(User('a-user')), "<User 'a-user'>")

    def test_fullname_is_last_and_firstname(self):
        self.assertEqual('Smith John', self.john.fullname())

    def test_fullname_is_only_first_or_lastname_if_other_is_missing(self):
        self.assertEqual('Bob', self.bob.fullname())
        self.assertEqual('Smith', self.jack.fullname())

    def test_fullname_is_userid_if_no_name_given(self):
        self.assertEqual('admin', self.admin.fullname())

    def test_label_is_the_fullname_with_username_in_braces(self):
        sammy = User('sammy', firstname='Samuel', lastname='Jackson', username="sjackson")
        self.assertEqual('Jackson Samuel (sjackson)', sammy.label())

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

    def test_supports_non_ascii_firstname_and_lastname(self):
        self.john.firstname = u'J\xf6hn'
        self.john.lastname = u'Sm\xe4th'

        self.assertEqual(u'Sm\xe4th J\xf6hn (john)', self.john.label())
        self.assertEqual(u'Sm\xe4th J\xf6hn', self.john.fullname())

    def test_supports_non_ascii_userid(self):
        self.john.userid = u'J\xf6hn'
        self.assertEqual("<User u'J\\xf6hn'>", str(self.john))

    def test_supports_non_ascii_username(self):
        self.john.username = u'J\xf6hn'
        self.assertEqual(u'Smith John (J\xf6hn)', self.john.label())


class TestUseridUsernameMappings(IntegrationTestCase):

    def setUp(self):
        super(TestUseridUsernameMappings, self).setUp()
        self.session = create_session()
        self.sammy = User('sammy', username="sjackson", external_id="foo")
        self.session.add(self.sammy)
        self.session.flush()

    def test_userid_to_username(self):
        self.assertEqual('sjackson', userid_to_username('sammy'))

    def test_userid_to_username_is_cached(self):
        self.assertEqual('sjackson', userid_to_username('sammy'))
        self.sammy.username = "samuel.jackson"
        self.assertEqual('sjackson', userid_to_username('sammy'))
        update_sync_stamp(self.portal)
        self.assertEqual('samuel.jackson', userid_to_username('sammy'))

    def test_username_to_userid(self):
        self.assertEqual('sammy', username_to_userid('sjackson'))

    def test_username_to_userid_is_cached(self):
        self.assertEqual('sammy', username_to_userid('sjackson'))
        self.sammy.userid = "sam"
        self.assertEqual('sammy', username_to_userid('sjackson'))
        update_sync_stamp(self.portal)
        self.assertEqual('sam', username_to_userid('sjackson'))
