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
    def test_shows_archived_organizations(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))
        create(Builder('archived_organization')
               .having(contact=organization,
                       name=u'habegger b\xfchlmann & co'))

        browser.login().open(organization.get_url())

        old_name = browser.css(
            '#contactHistory .contact_details').first.lists()[1]
        self.assertEquals(['Name', u'habegger b\xfchlmann & co'], old_name)

    @browsing
    def test_shows_addresses_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('address')
               .for_contact(organization)
               .labeled('Hauptsitz')
               .having(street=u'Dammweg 9', zip_code=u'3013', city=u'Bern',
                       country=u'Schweiz'))
        create(Builder('address')
               .for_contact(organization)
               .labeled('Standort Romandie')
               .having(street=u'S\xfcdweststrasse 24',
                       zip_code=u'1700', city=u'Fribourg'))

        browser.login().open(organization.get_url())

        self.assertEquals([u'Hauptsitz', u'Standort Romandie'],
                          browser.css('.address dt').text)
        self.assertEquals([u'Dammweg 9\n3013 Bern\nSchweiz',
                           u'S\xfcdweststrasse 24\n1700 Fribourg'],
                          browser.css('.address dd').text)

    @browsing
    def test_shows_archived_addresses_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('archived_address')
               .for_contact(organization)
               .labeled('Hauptsitz')
               .having(street=u'Engehaldenstrasse 42', zip_code=u'3012',
                       city=u'Bern', country=u'Schweiz'))

        browser.login().open(organization.get_url())

        self.assertEquals([u'Hauptsitz'],
                          browser.css('#contactHistory .address dt').text)
        self.assertEquals([u'Engehaldenstrasse 42\n3012 Bern\nSchweiz'],
                          browser.css('#contactHistory .address dd').text)

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
    def test_shows_archived_phonenumbers_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('archived_phonenumber')
               .for_contact(organization)
               .labeled('Support')
               .having(phone_number=u'012 34 56 78'))

        browser.login().open(organization.get_url())

        self.assertEquals([u'Support'],
                          browser.css('#contactHistory .phone_number dt').text)
        self.assertEquals(['012 34 56 78'],
                          browser.css('#contactHistory .phone_number dd').text)

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
                          browser.css('.mail dd a').text)
        self.assertEquals(
            [u'mailto:info@example.com', u'mailto:support@example.com'],
            [link.get('href') for link in browser.css('.mail dd a')])

    @browsing
    def test_shows_archived_email_addresses_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('archived_mail_addresses')
               .for_contact(organization)
               .labeled('Sales')
               .having(address=u'sales@example.com'))

        browser.login().open(organization.get_url())

        self.assertEquals([u'Sales'],
                          browser.css('#contactHistory .mail dt').text)
        self.assertEquals([u'sales@example.com'],
                          browser.css('#contactHistory .mail dd a').text)
        self.assertEquals(
            u'mailto:sales@example.com',
            browser.css('#contactHistory .mail dd a').first.get('href'))

    @browsing
    def test_lists_all_related_persons_alphabetically(self, browser):
        org1 = create(Builder('organization').named(u'4teamwork AG'))
        org2 = create(Builder('organization').named(u'Meier Ag'))

        create(Builder('person')
               .having(firstname=u'Peter', lastname=u'M\xfcller')
               .in_orgs([(org1, 'CEO'), (org2, 'VR-Mitglied')]))
        create(Builder('person')
               .having(firstname=u'Hans', lastname=u'Meier')
               .in_orgs([(org2, 'Sachbearbeiter')]))
        create(Builder('person')
               .having(firstname=u'Sandra', lastname=u'Muster')
               .in_orgs([(org1, u'Stellvertretende F\xfchrung')]))
        create(Builder('person')
               .having(firstname=u'Sandra', lastname=u'Meier')
               .in_orgs([(org1, u'CFO')]))

        browser.login().open(org1.get_url())

        self.assertEquals(
            ['Meier Sandra', 'Muster Sandra', u'M\xfcller Peter'],
            browser.css('.persons .name').text)
        self.assertEquals(
            [u'CFO', u'Stellvertretende F\xfchrung', u'CEO'],
            browser.css('.persons .function').text)

    @browsing
    def test_group_related_persons_by_active_state(self, browser):
        org1 = create(Builder('organization').named(u'4teamwork AG'))

        create(Builder('person')
               .having(firstname=u'Peter', lastname=u'M\xfcller')
               .in_orgs([(org1, 'CEO')]))
        create(Builder('person')
               .having(firstname=u'Sandra', lastname=u'Muster',
                       is_active=False)
               .in_orgs([(org1, u'Stellvertretende F\xfchrung')]))
        create(Builder('person')
               .having(firstname=u'Sandra', lastname=u'Meier')
               .in_orgs([(org1, u'CFO')]))

        browser.login().open(org1.get_url())

        self.assertEquals(['Meier Sandra', u'M\xfcller Peter'],
                          browser.css('.active_persons .name').text)
        self.assertEquals(['Muster Sandra'],
                          browser.css('.inactive_persons .name').text)

    @browsing
    def test_shows_linked_urls_prefixed_with_label(self, browser):
        organization = create(Builder('organization').named(u'4teamwork'))

        create(Builder('url')
               .for_contact(organization)
               .labeled('Blog')
               .having(url=u'http://www.peters-blog.example.com'))
        create(Builder('url')
               .for_contact(organization)
               .labeled('Homepage')
               .having(url=u'https://peters-homepage.example.com'))

        browser.login().open(self.contactfolder, view=organization.wrapper_id)

        self.assertEquals([u'Blog', u'Homepage'], browser.css('.url dt').text)
        links = browser.css('.url dd a')
        self.assertEquals([u'http://www.peters-blog.example.com',
                           u'https://peters-homepage.example.com'],
                          [link.text for link in links])
        self.assertEquals(['http://www.peters-blog.example.com',
                           'https://peters-homepage.example.com'],
                          [link.get('href') for link in links])

    @browsing
    def test_related_persons_are_linked_to_person_view(self, browser):
        org1 = create(Builder('organization').named(u'4teamwork AG'))
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller')
                       .in_orgs([(org1, 'CEO')]))

        browser.login().open(org1.get_url())

        self.assertEquals(
            peter.get_url(),
            browser.css('.persons .name > a').first.get('href'))
