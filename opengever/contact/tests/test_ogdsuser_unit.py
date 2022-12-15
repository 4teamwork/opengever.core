from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.ogdsuser import AddressAdapter
from opengever.contact.ogdsuser import MailAddressAdapter
from opengever.contact.ogdsuser import PhoneNumberAdapter
from opengever.contact.ogdsuser import URLAdapter
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.testing import MEMORY_DB_LAYER
from opengever.testing.builders.base import TEST_USER_ID
import unittest


class TestOgdsUserToContactAdapter(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestOgdsUserToContactAdapter, self).setUp()
        self.session = self.layer.session
        self.adapter = create(Builder('ogds_user')
                              .having(**OGDS_USER_ATTRIBUTES)
                              .as_contact_adapter())

    def test_title(self):
        self.assertEqual(u'M\xfcller Peter (test_user_1_)',
                         self.adapter.get_title())
        self.assertEqual(u'M\xfcller Peter',
                         self.adapter.get_title(with_former_id=False))

    def test_id(self):
        self.assertEqual(TEST_USER_ID, self.adapter.id)

    def get_css_class(self):
        self.assertEqual('contenttype-person', self.adapter.get_css_class())

    def test_description(self):
        self.assertEqual(u'nix', self.adapter.description)

    def test_salutation(self):
        self.assertEqual(u'Herr', self.adapter.salutation)

    def test_firstname(self):
        self.assertEqual(u'Peter', self.adapter.firstname)

    def test_lastname(self):
        self.assertEqual(u'M\xfcller', self.adapter.lastname)

    def test_addresses(self):
        self.assertEqual(
            [AddressAdapter(TEST_USER_ID, 1,
                            u'M\xfcller Peter',
                            u'Kappelenweg 13, Postfach 1234',
                            u'1234',
                            u'Vorkappelen',
                            u'Schweiz')],
            self.adapter.addresses)

    def test_mail_addresses(self):
        self.assertEqual(
            [MailAddressAdapter(TEST_USER_ID, 1, u'foo@example.com'),
             MailAddressAdapter(TEST_USER_ID, 2, u'bar@example.com')],
            self.adapter.mail_addresses)

    def test_phonenumbers(self):
        self.assertEqual(
            [PhoneNumberAdapter(TEST_USER_ID, 1,
                                u'012 34 56 78', u'label_office'),
             PhoneNumberAdapter(TEST_USER_ID, 2,
                                u'012 34 56 77', u'label_fax'),
             PhoneNumberAdapter(TEST_USER_ID, 3,
                                u'012 34 56 76', u'label_mobile')],
            self.adapter.phonenumbers)

    def test_urls(self):
        self.assertEqual(
            [URLAdapter(TEST_USER_ID, 1, u'http://www.example.com')],
            self.adapter.urls)
