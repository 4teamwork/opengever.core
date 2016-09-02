from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPersonView(FunctionalTestCase):

    def setUp(self):
        super(TestPersonView, self).setUp()
        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

    @browsing
    def test_person_wrapper_wrap_corresponding_person_object(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        sandra = create(Builder('person')
                        .having(firstname=u'Sandra', lastname=u'Fl\xfcckiger'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        self.assertEquals([u'Peter M\xfcller'], browser.css('h1').text)

        browser.login().open(self.contactfolder, view=sandra.wrapper_id)
        self.assertEquals([u'Sandra Fl\xfcckiger'], browser.css('h1').text)

    @browsing
    def test_shows_fullname_as_title(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        self.assertEquals([u'Peter M\xfcller'], browser.css('h1').text)

    @browsing
    def test_shows_personal_information_as_vertical_table(self, browser):
        peter = create(Builder('person')
                       .having(salutation='Herr',
                               firstname=u'Peter',
                               lastname=u'M\xfcller',
                               academic_title='Dr. rer. nat.'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        table = browser.css('.contact_details').first

        [['Name', u'Peter M\xfcller'],
         ['Salutation', 'Herr'],
         ['Academic title', 'Dr. rer. nat.'],
         ['Addresses'],
         ['Mails'],
         ['Phonenumbers']]
        table.dicts()

    @browsing
    def test_shows_archived_personal_information(self, browser):
        peter = create(Builder('person')
                       .having(salutation='Herr',
                               firstname=u'Peter',
                               lastname=u'M\xfcller',
                               academic_title='Dr. rer. nat.'))
        archived_peter = create(Builder('archived_person').having(
                                contact=peter,
                                salutation='Herr',
                                firstname=u'Peter',
                                lastname=u'Hanssen',
                                academic_title='Magister'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        table = browser.css('#contactHistory .contact_details').first

        [['Name', u'Peter Hanssen'],
         ['Salutation', 'Herr'],
         ['Academic title', 'Magister']]
        table.dicts()

    @browsing
    def test_shows_addresses_prefixed_with_label(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        create(Builder('address')
               .for_contact(peter)
               .labeled('Arbeit')
               .having(street=u'Dammweg 9', zip_code=u'3013', city=u'Bern'))
        create(Builder('address')
               .for_contact(peter)
               .labeled('Privat')
               .having(street=u'S\xfcdweststrasse 24',
                       zip_code=u'6315', city=u'Ober\xe4geri'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)

        self.assertEquals([u'Arbeit', u'Privat'],
                          browser.css('.address dt').text)
        self.assertEquals([u'Dammweg 9\n3013 Bern',
                           u'S\xfcdweststrasse 24\n6315 Ober\xe4geri'],
                          browser.css('.address dd').text)

    @browsing
    def test_shows_archived_addresses_prefixed_with_label(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        create(Builder('archived_address')
               .for_contact(peter)
               .labeled('Wochenendhaus')
               .having(street=u'Waldstrasse 1', zip_code=u'1234',
                       city=u'Hintertupfigen'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)

        self.assertEquals([u'Wochenendhaus'],
                          browser.css('#contactHistory .address dt').text)
        self.assertEquals([u'Waldstrasse 1\n1234 Hintertupfigen'],
                          browser.css('#contactHistory .address dd').text)

    @browsing
    def test_shows_phonenumbers_prefixed_with_label(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        create(Builder('phonenumber')
               .for_contact(peter)
               .labeled('Mobile')
               .having(phone_number=u'099 578 97 48'))

        create(Builder('phonenumber')
               .for_contact(peter)
               .labeled('Arbeit')
               .having(phone_number=u'099 111 22 33'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)

        self.assertEquals([u'Mobile', u'Arbeit'],
                          browser.css('.phone_number dt').text)
        self.assertEquals(['099 578 97 48', '099 111 22 33'],
                          browser.css('.phone_number dd').text)

    @browsing
    def test_shows_archived_phonenumbers_prefixed_with_label(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        create(Builder('archived_phonenumber')
               .for_contact(peter)
               .labeled('Rotary Club')
               .having(phone_number=u'011 111 11 00'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)

        self.assertEquals([u'Rotary Club'],
                          browser.css('#contactHistory .phone_number dt').text)
        self.assertEquals(['011 111 11 00'],
                          browser.css('#contactHistory .phone_number dd').text)

    @browsing
    def test_shows_email_addresses_prefixed_with_label(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        create(Builder('mailaddress')
               .for_contact(peter)
               .labeled('Privat')
               .having(address=u'peter.m@example.com'))

        create(Builder('mailaddress')
               .for_contact(peter)
               .labeled('Arbeit')
               .having(address=u'peter.work@example.com'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)

        self.assertEquals([u'Privat', u'Arbeit'],
                          browser.css('.mail dt').text)
        self.assertEquals([u'peter.m@example.com', u'peter.work@example.com'],
                          browser.css('.mail dd').text)

    @browsing
    def test_shows_archived_email_addresses_prefixed_with_label(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        create(Builder('archived_mail_addresses')
               .for_contact(peter)
               .labeled('Privat')
               .having(address=u'peterli@example.com'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)

        self.assertEquals([u'Privat'],
                          browser.css('#contactHistory .mail dt').text)
        self.assertEquals([u'peterli@example.com'],
                          browser.css('#contactHistory .mail dd').text)

    @browsing
    def test_shows_urls_prefixed_with_label(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        create(Builder('url')
               .for_contact(peter)
               .labeled('Blog')
               .having(url=u'peters-blog.example.com'))
        create(Builder('url')
               .for_contact(peter)
               .labeled('Homepage')
               .having(url=u'peters-homepage.example.com'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)

        self.assertEquals([u'Blog', u'Homepage'], browser.css('.url dt').text)
        self.assertEquals(
            [u'peters-blog.example.com', u'peters-homepage.example.com'],
            browser.css('.url dd').text)

    @browsing
    def test_list_all_of_the_users_organizations_alphabetically(self, browser):
        org1 = create(Builder('organization').named(u'Jaeger & Heike GmbH'))
        create(Builder('organization').named(u'Schuhmacher Peter AG'))
        org3 = create(Builder('organization').named(u'Albert B & N SA'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller')
                       .in_orgs([(org1, 'CEO'),
                                 (org3, u'Stellvertretende F\xfchrung')]))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        self.assertEquals(
            ['Albert B & N SA', 'Jaeger & Heike GmbH'],
            browser.css('.organizations .name').text)

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        self.assertEquals(
            [u'Stellvertretende F\xfchrung', u'CEO'],
            browser.css('.organizations .function').text)

    @browsing
    def test_related_organizations_are_linked_to_organization_view(self, browser):
        org1 = create(Builder('organization').named(u'4teamwork AG'))
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller')
                       .in_orgs([(org1, 'CEO')]))

        browser.login().open(peter.get_url())

        self.assertEquals(
            org1.get_url(),
            browser.css('.organizations .name > a').first.get('href'))
