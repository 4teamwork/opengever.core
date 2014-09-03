from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized
from zope.i18n import translate
import transaction


class TestReferencePrefixManager(FunctionalTestCase):

    def setUp(self):
        super(TestReferencePrefixManager, self).setUp()
        self.grant('Manager')

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository')
            .titled(u'Weiterbildung')
            .within(self.root))
        self.repo1 = create(Builder('repository')
                        .titled("One")
                        .within(self.repo))
        self.repo2 = create(Builder('repository')
                        .titled("Two")
                        .within(self.repo))

        self.reference_manager = ReferenceNumberPrefixAdpater(self.repo)
        # move repo1 to prefix 3 which leaves prefix 1 unused
        self.reference_manager.set_number(self.repo1, 3)
        transaction.commit()

    @browsing
    def test_manager_lists_used_and_unused_prefixes(self, browser):
        browser.login().open(self.repo, view='referenceprefix_manager')

        table = browser.css('#reference_prefix_manager_table').first.lists()
        self.assertEquals([['1', 'One', 'Unlock'],
                           ['2', 'Two', 'In use'],
                           ['3', 'One', 'In use']], table)

    @browsing
    def test_manager_deletes_unused_prefix_when_button_is_clicked(self, browser):
        browser.login().open(self.repo, view='referenceprefix_manager')

        # works because we only have one unlock button
        browser.css('.unlock').first.click()

        table = browser.css('#reference_prefix_manager_table').first.lists()

        self.assertEquals([['2', 'Two', 'In use'],
                           ['3', 'One', 'In use']], table)

    def test_manager_throws_error_when_delete_request_for_used_prefix_occurs(self):
        self.assertRaises(Exception, self.reference_manager.free_number, (2))

    @browsing
    def test_manager_shows_default_message_when_no_repositorys_available(self, browser):
        browser.login().open(self.repo1, view='referenceprefix_manager')

        self.assertEquals(
            'No nested repositorys available.',
            browser.css('#reference_prefix_manager_table tbody').first.text)

    @browsing
    def test_manager_is_hided_from_user_without_permission(self, browser):
        self.grant('Contributor')

        with self.assertRaises(Unauthorized):
            browser.login().open(self.repo1, view='referenceprefix_manager')

    @browsing
    def test_unlock_event_gets_logged_in_journal(self, browser):
        browser.login().open(self.repo, view='referenceprefix_manager')
        browser.css('.unlock').first.click()

        # get last journal entry
        journal = get_journal_entry(self.root, entry=-1)

        self.assertEquals(
            'Unlocked prefix 1 in weiterbildung.',
            translate(journal.get('action').get('title')))
