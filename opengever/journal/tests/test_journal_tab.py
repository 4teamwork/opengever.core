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

            expected = [['Time', 'Title', 'Changed by', 'Comments'],
                        ['12.08.2016 01:00',
                         'Dossier modified: dossier-1',
                         'Test User (test_user_1_)', ''],
                        ['12.08.2016 01:00',
                         u'Document added: Anfrage M\xfcller',
                         'Test User (test_user_1_)', ''],
                        ['12.08.2016 01:00',
                         'Dossier added: dossier-1',
                         'Test User (test_user_1_)', '']]

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

            expected = [['Time', 'Title', 'Changed by', 'Comments'],
                        ['12.08.2016 01:00',
                         u'Document added: Anfrage M\xfcller',
                         'Test User (test_user_1_)', '']]
            self.assertEquals(expected, browser.css('.listing').first.lists())
