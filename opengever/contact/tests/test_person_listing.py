from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPersonListing(FunctionalTestCase):

    labels = ['Salutation', 'Academic title', 'First name',
              'Last name', 'Active', 'Former contact ID']

    def setUp(self):
        super(TestPersonListing, self).setUp()

        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

        self.peter = create(Builder('person')
                            .having(salutation='Herr',
                                    firstname=u'Peter',
                                    lastname=u'M\xfcller',
                                    academic_title='Dr. rer. nat.',
                                    former_contact_id=112233))
        self.sandra = create(Builder('person')
                             .having(salutation='Frau',
                                     firstname=u'Sandra',
                                     lastname=u'Albert',
                                     is_active=False))
        self.max = create(Builder('person')
                          .having(salutation='Frau',
                                  firstname=u'Sandra',
                                  lastname=u'Mustermann',
                                  former_contact_id=445566))

    @browsing
    def test_lists_only_active_persons_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons')

        self.assertEquals(
            [self.labels,
             ['Frau', '', 'Sandra', 'Mustermann', 'Yes', '445566'],
             ['Herr', 'Dr. rer. nat.', 'Peter',
              u'M\xfcller', 'Yes', '112233']],
            browser.css('.listing').first.lists())

    @browsing
    def test_includes_inactive_persons_with_the_all_filter(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons',
            data={'person_state_filter': 'filter_all'})

        self.assertEquals(
            [self.labels,
             ['Frau', '', 'Sandra', 'Albert', 'No', ''],
             ['Frau', '', 'Sandra', 'Mustermann', 'Yes', '445566'],
             ['Herr', 'Dr. rer. nat.', 'Peter',
              u'M\xfcller', 'Yes', '112233']],
            browser.css('.listing').first.lists())

    @browsing
    def test_sorts_on_lastname_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons',
            data={'person_state_filter': 'filter_all'})

        table = browser.css('.listing').first
        self.assertEquals(
            ['Albert', 'Mustermann', u'M\xfcller'],
            [row.get('Last name') for row in table.dicts()])

    @browsing
    def test_first_and_lastname_are_linked_to_person_view(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons')

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/contact-1/view',
            browser.find('Peter').get('href'))

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/contact-1/view',
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
    def test_filtering_on_firstname(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-persons',
            data={'searchable_text': 'sandra',
                  'person_state_filter': 'filter_all'})

        self.assertEquals(
            [self.labels,
             ['Frau', '', 'Sandra', 'Albert', 'No', ''],
             ['Frau', '', 'Sandra', 'Mustermann', 'Yes', '445566']],
            browser.css('.listing').first.lists())

    @browsing
    def test_filtering_on_firstname_and_lastname(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-persons',
            data={'searchable_text': 'Sandra Alb',
                  'person_state_filter': 'filter_all'})

        self.assertEquals(
            [self.labels,
             ['Frau', '', 'Sandra', 'Albert', 'No', '']],
            browser.css('.listing').first.lists())
