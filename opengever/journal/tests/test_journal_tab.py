from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import FunctionalTestCase


class TestJournalTab(FunctionalTestCase):

    def setUp(self):
        super(TestJournalTab, self).setUp()

    @browsing
    def test_list_all_journal_entries(self, browser):
        with freeze(datetime(2016, 8, 12)):
            self.dossier = create(Builder('dossier'))
            self.document = create(Builder('document')
                                   .titled(u'Anfrage M\xfcller')
                                   .within(self.dossier))

            browser.login().open(self.dossier, view=u'tabbedview_view-journal')

            expected = [
                ['Time', 'Title', 'Changed by', 'Comments', 'References'],
                ['12.08.2016 01:00',
                 'Dossier modified: dossier-1',
                 'Test User (test_user_1_)', '', ''],
                ['12.08.2016 01:00',
                 u'Document added: Anfrage M\xfcller',
                 'Test User (test_user_1_)', '', ''],
                ['12.08.2016 01:00',
                 'Dossier added: dossier-1',
                 'Test User (test_user_1_)', '', '']]

            self.assertEquals(expected, browser.css('.listing').first.lists())

    @browsing
    def test_listing_supports_filtering_on_title(self, browser):
        with freeze(datetime(2016, 8, 12)):
            self.dossier = create(Builder('dossier'))
            self.document = create(Builder('document')
                                   .titled(u'Anfrage M\xfcller')
                                   .within(self.dossier))
            browser.login().open(self.dossier, view=u'tabbedview_view-journal',
                                 data={'searchable_text': u'M\xfcl'})

            expected = [
                ['Time', 'Title', 'Changed by', 'Comments', 'References'],
                ['12.08.2016 01:00',
                 u'Document added: Anfrage M\xfcller',
                 'Test User (test_user_1_)', '', '']]
            self.assertEquals(expected, browser.css('.listing').first.lists())

    @browsing
    def test_add_journal_entry_link_is_only_shown_when_dosier_can_be_modified(self, browser):
        dossier_a = create(Builder('dossier'))
        dossier_b = create(Builder('dossier')
                           .in_state('dossier-state-resolved'))

        browser.login().open(dossier_a, view=u'tabbedview_view-journal')
        self.assertEquals(['Add journal entry'],
                          browser.css('.add_journal_entry').text)

        browser.login().open(dossier_b, view=u'tabbedview_view-journal')
        self.assertEquals([], browser.css('.add_journal_entry'))
