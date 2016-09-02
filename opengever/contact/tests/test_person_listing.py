from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPersonListing(FunctionalTestCase):

    def setUp(self):
        super(TestPersonListing, self).setUp()

        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

        self.peter = create(Builder('person')
                            .having(salutation='Herr',
                                    firstname=u'Peter',
                                    lastname=u'M\xfcller',
                                    academic_title='Dr. rer. nat.'))
        self.sandra = create(Builder('person')
                             .having(salutation='Frau',
                                     firstname=u'Sandra',
                                     lastname=u'Albert',
                                     is_active=False))
        self.max = create(Builder('person')
                          .having(salutation='Frau',
                                  firstname=u'Sandra',
                                  lastname=u'Mustermann'))

    @browsing
    def test_lists_only_active_persons_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons')

        self.assertEquals(
            [['Salutation', 'Academic title', 'Firstname',
              'Lastname', 'Active', 'Organizations'],
             ['Frau', '', 'Sandra', 'Mustermann', 'Yes', ''],
             ['Herr', 'Dr. rer. nat.', 'Peter', u'M\xfcller', 'Yes', '']],
            browser.css('.listing').first.lists())

    @browsing
    def test_includes_inactive_persons_with_the_all_filter(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons',
            data={'person_state_filter': 'filter_all'})

        self.assertEquals(
            [['Salutation', 'Academic title', 'Firstname',
              'Lastname', 'Active', 'Organizations'],
             ['Frau', '', 'Sandra', 'Albert', 'No', ''],
             ['Frau', '', 'Sandra', 'Mustermann', 'Yes', ''],
             ['Herr', 'Dr. rer. nat.', 'Peter', u'M\xfcller', 'Yes', '']],
            browser.css('.listing').first.lists())

    @browsing
    def test_sorts_on_lastname_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons',
            data={'person_state_filter': 'filter_all'})

        table = browser.css('.listing').first
        self.assertEquals(
            ['Albert', 'Mustermann', u'M\xfcller'],
            [row.get('Lastname') for row in table.dicts()])

    @browsing
    def test_first_and_lastname_are_linked_to_person_view(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons')

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/person-1/view',
            browser.find('Peter').get('href'))

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/person-1/view',
            browser.find(u'M\xfcller').get('href'))

    @browsing
    def test_contact_links_are_escaped(self, browser):
        self.bold = create(Builder('person')
                           .having(firstname=u'Usain',
                                   lastname=u'<b>Bold</b>'))

        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons')

        row1 = browser.css('.listing').first.rows[1]
        self.assertEquals('<b>Bold</b>', row1.css('td')[-3].text)

    @browsing
    def test_organizations_are_linked_and_sepearated_by_comma(self, browser):
        self.org1 = create(Builder('organization').named(u'Meier AG'))
        self.org2 = create(Builder('organization').named(u'Sophie SA'))
        create(Builder('org_role').having(
            person=self.sandra, organization=self.org1))
        create(Builder('org_role').having(
            person=self.sandra, organization=self.org2))

        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-persons',
            data={'person_state_filter': 'filter_all'})

        row = browser.css('.listing').first.rows[1]

        self.assertEquals(
            ['Frau', '', 'Sandra', 'Albert', 'No', u'Meier AG, Sophie SA'],
            row.css('td').text)
        self.assertEquals(self.org1.get_url(),
                          row.find('Meier AG').get('href'))
        self.assertEquals(self.org2.get_url(),
                          row.find('Sophie SA').get('href'))

    @browsing
    def test_filtering_on_firstname(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-persons',
            data={'searchable_text': 'sandra',
                  'person_state_filter': 'filter_all'})

        self.assertEquals(
            [['Salutation', 'Academic title', 'Firstname',
              'Lastname', 'Active', 'Organizations'],
             ['Frau', '', 'Sandra', 'Albert', 'No', ''],
             ['Frau', '', 'Sandra', 'Mustermann', 'Yes', '']],
            browser.css('.listing').first.lists())

    @browsing
    def test_filtering_on_firstname_and_lastname(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-persons',
            data={'searchable_text': 'Sandra Alb',
                  'person_state_filter': 'filter_all'})

        self.assertEquals(
            [['Salutation', 'Academic title', 'Firstname',
              'Lastname', 'Active', 'Organizations'],
             ['Frau', '', 'Sandra', 'Albert', 'No', '']],
            browser.css('.listing').first.lists())
