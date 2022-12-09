from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.contact.interfaces import IContactSettings
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.core.testing import toggle_feature
from opengever.testing import FunctionalTestCase
from opengever.testing import SolrIntegrationTestCase
from opengever.testing.helpers import get_contacts_token


class TestManualJournalEntry(FunctionalTestCase):

    def setUp(self):
        super(TestManualJournalEntry, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.contactfolder = create(Builder('contactfolder'))
        toggle_feature(IContactSettings, enabled=True)

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
             'Title': 'Phone call',
             'Comments': u'Anfrage bez\xfcglich dem Jahr 2016 von Herr Meier',
             'References': u'',
             'Time': '09.12.2016 09:40'},
            browser.css('.listing').first.rows[2].dict())

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
            'Related documents': [doc1, doc2]})
        browser.css('#form-buttons-add').first.click()

        browser.open(self.dossier, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]

        self.assertEquals(u'Documents Testdokum\xe4nt A Testdokum\xe4nt B',
                          row.dict().get('References'))

        browser.click_on(u'Testdokum\xe4nt B')
        self.assertEquals(doc2.absolute_url(), browser.url)

    @browsing
    def test_cancel_the_form_redirects_back_to_journal_tab(self, browser):
        browser.login().open(self.dossier, view='add-journal-entry')
        browser.css('#form-buttons-cancel').first.click()

        self.assertEquals(
            '{}#journal'.format(self.dossier.absolute_url()), browser.url)

    @browsing
    def test_contact_field_is_hidden_when_contact_feature_is_disabled(self, browser):
        toggle_feature(IContactSettings, enabled=False)

        browser.login().open(self.dossier, view='add-journal-entry')

        self.assertIsNone(browser.find_field_by_text('Contacts'))


class TestManualJournalEntrySolr(SolrIntegrationTestCase):

    @browsing
    def test_only_documents_from_the_dossier_are_selectable(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.resolvable_dossier, view='add-journal-entry')
        browser.fill(
            {'form.widgets.related_documents.widgets.query': self.resolvable_document.title}).submit()

        self.assertEquals(
            [self.resolvable_document.title],
            browser.css('#form-widgets-related_documents-autocomplete .option').text)

        browser.open(self.dossier, view='add-journal-entry')
        browser.fill(
            {'form.widgets.related_documents.widgets.query': self.resolvable_document.title}).submit()

        self.assertEquals(
            [],
            browser.css('#form-widgets-related_documents-autocomplete .option').text)
