from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import Contact
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestOrganization(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_is_contact(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        self.assertTrue(isinstance(organization, Contact))
        self.assertEquals('organization', organization.contact_type)

    def test_is_active_by_default(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        self.assertTrue(organization.is_active)

    def test_organization_can_have_multiple_addresses(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        address1 = create(Builder('address')
                          .for_contact(organization)
                          .labeled(u'Work')
                          .having(street=u'Dammweg 9', zip_code=u'3013',
                                  city=u'Bern'))

        address2 = create(Builder('address')
                          .for_contact(organization)
                          .labeled(u'Home')
                          .having(street=u'Musterstrasse 283',
                                  zip_code=u'1700',
                                  city=u'Fribourg'))

        self.assertEquals([address1, address2], organization.addresses)

    def test_organization_can_have_multiple_mail_addresses(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        loc1 = create(Builder('mailaddress')
                      .for_contact(organization)
                      .labeled(u'Home')
                      .having(address=u'loc1@example.com'))

        loc2 = create(Builder('mailaddress')
                      .for_contact(organization)
                      .labeled(u'Work')
                      .having(address=u'loc2@example.com'))

        self.assertEquals([loc1, loc2], organization.mail_addresses)
        self.assertEquals([u'loc1@example.com', u'loc2@example.com'],
                          [mail.address for mail in organization.mail_addresses])

    def test_organization_can_have_multiple_phonenumbers(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        home = create(Builder('phonenumber')
                      .for_contact(organization)
                      .labeled(u'Home')
                      .having(phone_number=u'+41791234566'))

        boss = create(Builder('phonenumber')
                      .for_contact(organization)
                      .labeled(u'Work')
                      .having(phone_number=u'0315110000'))

        self.assertEquals([home, boss], organization.phonenumbers)
        self.assertEquals([u'+41791234566', u'0315110000'],
                          [phone.phone_number for phone in organization.phonenumbers])

    def test_organization_can_have_multiple_urls(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        info = create(Builder('url')
                      .for_contact(organization)
                      .labeled(u'Info')
                      .having(url=u'http://example.org'))

        gever = create(Builder('url')
                       .for_contact(organization)
                       .labeled(u'Info')
                       .having(url=u'http://example.com'))

        self.assertEquals([info, gever], organization.urls)
        self.assertEquals([u'http://example.org',
                           u'http://example.com'],
                          [url.url for url in organization.urls])

    def test_title_is_name(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))
        self.assertEquals(u'4teamwork AG', organization.get_title())

    def test_title_is_extended_with_former_id_in_brackets_when_flag_is_set(self):
        teamwork = create(Builder('organization').named(u'4teamwork AG'))
        meier = create(Builder('organization')
                       .having(former_contact_id=123456)
                       .named(u'Meier AG'))

        self.assertEquals(u'4teamwork AG',
                          teamwork.get_title(with_former_id=True))
        self.assertEquals(u'Meier AG [123456]',
                          meier.get_title(with_former_id=True))
