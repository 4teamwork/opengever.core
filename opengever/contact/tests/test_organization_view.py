from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestOrganizationView(FunctionalTestCase):

    def setUp(self):
        super(TestOrganizationView, self).setUp()
        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

    @browsing
    def test_organization_wrapper_wraps_organization_model(self, browser):
        org1 = create(Builder('organization').named(u'Meier AG'))
        org2 = create(Builder('organization').named(u'4teamwork AG'))

        browser.login().open(self.contactfolder, view=org1.wrapper_id)
        self.assertEquals([u'Meier AG'], browser.css('h1').text)

        browser.login().open(self.contactfolder, view=org2.wrapper_id)
        self.assertEquals([u'4teamwork AG'], browser.css('h1').text)

    @browsing
    def test_body_contains_person_type_class(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        browser.login().open(organization.get_url())
        self.assertIn('portaltype-opengever-contact-organization',
                      browser.css('body').first.get('class'))

    @browsing
    def test_shows_addresses_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('address')
               .for_contact(organization)
               .labeled('Hauptsitz')
               .having(street=u'Dammweg 9', zip_code=u'3013', city=u'Bern'))
        create(Builder('address')
               .for_contact(organization)
               .labeled('Standort Romandie')
               .having(street=u'S\xfcdweststrasse 24',
                       zip_code=u'1700', city=u'Fribourg'))

        browser.login().open(organization.get_url())

        self.assertEquals([u'Hauptsitz', u'Standort Romandie'],
                          browser.css('.address dt').text)
        self.assertEquals([u'Dammweg 9\n3013 Bern',
                           u'S\xfcdweststrasse 24\n1700 Fribourg'],
                          browser.css('.address dd').text)

    @browsing
    def test_shows_phonenumbers_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('phonenumber')
               .for_contact(organization)
               .labeled('Zentrale')
               .having(phone_number=u'099 578 97 48'))

        create(Builder('phonenumber')
               .for_contact(organization)
               .labeled('Support')
               .having(phone_number=u'099 111 22 33'))

        browser.login().open(organization.get_url())

        self.assertEquals([u'Zentrale', u'Support'],
                          browser.css('.phone_number dt').text)
        self.assertEquals(['099 578 97 48', '099 111 22 33'],
                          browser.css('.phone_number dd').text)

    @browsing
    def test_shows_email_addresses_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('mailaddress')
               .for_contact(organization)
               .labeled('Info')
               .having(address=u'info@example.com'))

        create(Builder('mailaddress')
               .for_contact(organization)
               .labeled('Support')
               .having(address=u'support@example.com'))

        browser.login().open(organization.get_url())

        self.assertEquals([u'Info', u'Support'],
                          browser.css('.mail dt').text)
        self.assertEquals([u'info@example.com', u'support@example.com'],
                          browser.css('.mail dd').text)
