from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import get_contacts_vocabulary


def get_token(obj):
    return get_contacts_vocabulary().getTerm(obj).token


class TestManualJournalEntry(FunctionalTestCase):

    def setUp(self):
        super(TestManualJournalEntry, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.contactfolder = create(Builder('contactfolder'))

    @browsing
    def test_adds_entry_to_context_journal(self, browser):

        with freeze(datetime(2016, 12, 9, 9, 40)):
            browser.login().open(self.dossier, view='add-journal-entry')
            browser.fill({
                'Category': u'phone-call',
                'Comment': u'Anfrage bez\xfcglich dem Jahr 2016 von Herr Meier'
            })
            browser.css('#form-buttons-add').first.click()

        self.assertEquals('http://nohost/plone/dossier-1#journal', browser.url)

        browser.open(self.dossier, view=u'tabbedview_view-journal')
        self.assertEquals(
            {'Changed by': 'Test User (test_user_1_)',
             'Title': 'Manual entry: Phone call',
             'Comments': u'Anfrage bez\xfcglich dem Jahr 2016 von Herr Meier',
             'References': u'',
             'Time': '09.12.2016 09:40'},
            browser.css('.listing').first.rows[1].dict())

    @browsing
    def test_selected_documents_are_listed_and_linked_in_the_references_column(self, browser):
        doc1 = create(Builder('document')
                      .titled(u'Testdokum\xe4nt A')
                      .within(self.dossier))
        doc2 = create(Builder('document')
                      .titled(u'Testdokum\xe4nt B')
                      .within(self.dossier))

        browser.login().open(self.dossier, view='add-journal-entry')
        browser.fill({
            'Category': u'phone-call',
            'Comment': u'Anfrage bez\xfcglich dem Jahr 2016 von Herr Meier',
            'Related Documents': [doc1, doc2]})
        browser.css('#form-buttons-add').first.click()

        browser.open(self.dossier, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]

        self.assertEquals(u'Documents Testdokum\xe4nt A Testdokum\xe4nt B',
                          row.dict().get('References'))

        browser.click_on(u'Testdokum\xe4nt B')
        self.assertEquals(doc2.absolute_url(), browser.url)

    @browsing
    def test_selected_contacts_are_listed_and_linked_in_the_references_column(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'H\xfcgo', lastname='Boss'))

        meierag = create(Builder('organization').named(u'Meier AG'))

        browser.login().open(self.dossier, view='add-journal-entry')
        browser.fill({
            'Category': u'phone-call',
            'Comment': u'Anfrage bez\xfcglich dem Jahr 2016 von Herr Meier',
            'Contacts': [get_token(peter), get_token(meierag)]})
        browser.css('#form-buttons-add').first.click()

        browser.open(self.dossier, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]
        links = row.css('.contacts a')

        self.assertEquals(u'Contacts Boss H\xfcgo Meier AG',
                          row.dict().get('References'))

        self.assertEquals(
            ['http://nohost/plone/opengever-contact-contactfolder/contact-1',
             'http://nohost/plone/opengever-contact-contactfolder/contact-2'],
            [link.get('href') for link in links])
        self.assertEquals([u'Boss H\xfcgo', 'Meier AG'], links.text)
