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
                                     lastname=u'Albert'))
        self.max = create(Builder('person')
                          .having(salutation='Frau',
                                  firstname=u'Sandra',
                                  lastname=u'Mustermann'))

    @browsing
    def test_lists_all_persons(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons')

        self.assertEquals(
            [['Salutation', 'Academic title', 'Firstname', 'Lastname'],
             ['Frau', '', 'Sandra', 'Albert'],
             ['Frau', '', 'Sandra', 'Mustermann'],
             ['Herr', 'Dr. rer. nat.', 'Peter', u'M\xfcller']],
            browser.css('.listing').first.lists())

    @browsing
    def test_sorts_on_lastname_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-persons')

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
        self.assertEquals('<b>Bold</b>', row1.css('td')[-1].text)

    @browsing
    def test_filtering_on_firstname(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-persons',
            data={'searchable_text': 'sandra'})

        self.assertEquals(
            [['Salutation', 'Academic title', 'Firstname', 'Lastname'],
             ['Frau', '', 'Sandra', 'Albert'],
             ['Frau', '', 'Sandra', 'Mustermann']],
            browser.css('.listing').first.lists())

    @browsing
    def test_filtering_on_firstname_and_lastname(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-persons',
            data={'searchable_text': 'Sandra Alb'})

        self.assertEquals(
            [['Salutation', 'Academic title', 'Firstname', 'Lastname'],
             ['Frau', '', 'Sandra', 'Albert']],
            browser.css('.listing').first.lists())
