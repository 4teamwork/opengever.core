from datetime import datetime
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import FunctionalTestCase
from persistent.list import PersistentList
from plone.app.testing import TEST_USER_ID
from zope.annotation import IAnnotations
import transaction


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
    def test_listing_supports_filtering_on_comments(self, browser):
        with freeze(datetime(2016, 8, 12)):
            self.dossier = create(Builder('dossier'))
            entry = get_journal_entry(self.dossier)
            entry['comments'] = 'Lorem Ipsum'
            transaction.commit()
            browser.login().open(self.dossier, view=u'tabbedview_view-journal',
                                 data={'searchable_text': u'ipsum'})

            expected = [
                ['Time', 'Title', 'Changed by', 'Comments', 'References'],
                ['12.08.2016 01:00',
                 'Dossier added: dossier-1',
                 'Test User (test_user_1_)', 'Lorem Ipsum', '']]
            self.assertEquals(expected, browser.css('.listing').first.lists())

    @browsing
    def test_listing_supports_filtering_on_actor(self, browser):
        with freeze(datetime(2016, 8, 12)):
            self.dossier = create(Builder('dossier'))
            browser.login().open(self.dossier, view=u'tabbedview_view-journal',
                                 data={'searchable_text': u'Test_User'})

            expected = [
                ['Time', 'Title', 'Changed by', 'Comments', 'References'],
                ['12.08.2016 01:00',
                 'Dossier added: dossier-1',
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

    @browsing
    def test_add_journal_entry_is_xss_safe(self, browser):
        dossier = create(Builder('dossier'))

        browser.login().open(dossier, view=u'add-journal-entry')
        browser.fill({
            'Category': 'information',
            'Comment': '<img src="http://not.found/" onerror="script:alert(\'XSS\');" />'
        })
        browser.css('[name="form.buttons.add"]').first.click()
        statusmessages.assert_no_error_messages()

        browser.open(dossier, view=u'tabbedview_view-journal')
        self.assertIn(
            '&lt;img src="http://not.found/" onerror="script:alert(\'XSS\');" /&gt;',
            browser.contents)


class TestJournalTabSorting(FunctionalTestCase):

    def setUp(self):
        super(TestJournalTabSorting, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.annotations = IAnnotations(self.dossier)
        self.annotations[JOURNAL_ENTRIES_ANNOTATIONS_KEY] = PersistentList()

    def add_entry(self, title, time, actor=TEST_USER_ID):
        self.annotations[JOURNAL_ENTRIES_ANNOTATIONS_KEY].append(
            {'action': {'visible': True,
                        'type': 'Dossier changed',
                        'title': title},
             'comments': '',
             'actor': actor,
             'time': time})

    @browsing
    def test_sorting_on_creation_time(self, browser):
        self.add_entry('Entry 1', DateTime(2016, 1, 1, 11, 30))
        self.add_entry('Entry 2', DateTime(2016, 1, 1, 16, 30))
        self.add_entry('Entry 3', DateTime(2016, 1, 1, 10, 30))

        transaction.commit()

        # ascending
        browser.login().open(self.dossier,
                             view=u'tabbedview_view-journal',
                             data={'sort': 'time', 'dir': 'ASC'})
        self.assertEquals(
            ['Entry 3', 'Entry 1', 'Entry 2'],
            [row.get('Title') for row in browser.css('.listing').first.dicts()])

        # descending
        browser.login().open(self.dossier,
                             view=u'tabbedview_view-journal',
                             data={'sort': 'time', 'dir': 'DESC'})
        self.assertEquals(
            ['Entry 2', 'Entry 1', 'Entry 3'],
            [row.get('Title') for row in browser.css('.listing').first.dicts()])

    @browsing
    def test_sorting_on_actor_column(self, browser):
        create(Builder('ogds_user')
               .having(userid='peter.albrecht',
                       firstname=u'Peter',
                       lastname=u'Albrecht'))
        create(Builder('ogds_user')
               .having(userid='hans.fluckiger',
                       firstname=u'Fl\xfcckiger',
                       lastname=u'Hans'))

        self.add_entry('Entry 1', DateTime(), 'peter.albrecht')
        self.add_entry('Entry 2', DateTime(), 'hans.fluckiger')
        self.add_entry('Entry 3', DateTime(), 'peter.albrecht')
        transaction.commit()

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-journal',
                             data={'sort': 'actor', 'dir': 'ASC'})
        self.assertEquals(
            ['Albrecht Peter (peter.albrecht)',
             'Albrecht Peter (peter.albrecht)',
             u'Hans Fl\xfcckiger (hans.fluckiger)'],
            [row.get('Changed by') for row in browser.css('.listing').first.dicts()])

    @browsing
    def test_sorting_on_title(self, browser):
        self.add_entry('Entry B', DateTime())
        self.add_entry('Entry C', DateTime())
        self.add_entry('Entry A', DateTime())
        transaction.commit()

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-journal',
                             data={'sort': 'title', 'dir': 'ASC'})
        self.assertEquals(
            ['Entry A', 'Entry B', 'Entry C'],
            [row.get('Title') for row in browser.css('.listing').first.dicts()])
