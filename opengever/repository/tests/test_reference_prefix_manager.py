from ftw.builder import Builder
from ftw.builder import create
from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized
from zope.i18n import translate
import transaction



class TestReferencePrefixManager(FunctionalTestCase):
    use_browser = True

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

    def parse_manager_table_data(self):
        table = []
        for tr in self.browser.css("#content .listing tr"):
            row = []
            for i in range(0, 3):
                td = tr.target.getchildren()[i]
                text = td.text_content().strip()
                if text == '': # no text? then maybe a button.
                    text = td.getchildren()[0].value
                row.append(text)
            table.append(row)
        return table

    def test_manager_lists_used_and_unused_prefixes(self):
        self.browser.open('%s/referenceprefix_manager' % (self.repo.absolute_url()))
        table = self.parse_manager_table_data()

        self.assertEquals([
                ['1', 'One', 'Unlock'],
                ['2', 'Two', 'In use'],
                ['3', 'One', 'In use']
            ], table)

    def test_manager_deletes_unused_prefix_when_button_is_clicked(self):
        self.browser.open('%s/referenceprefix_manager' % (self.repo.absolute_url()))

        # works because we only have one unlock button
        self.browser.getLink("Unlock").click()

        table = self.parse_manager_table_data()

        self.assertEquals([
            ['2', 'Two', 'In use'],
            ['3', 'One', 'In use']
        ], table)

    def test_manager_throws_error_when_delete_request_for_used_prefix_occurs(self):
        self.assertRaises(Exception, self.reference_manager.free_number, (2))

    def test_manager_shows_default_message_when_no_repositorys_available(self):
        self.browser.open('%s/referenceprefix_manager' % (self.repo1.absolute_url()))

        prefixmanager = self.browser.css("#content td")

        self.assertEquals(
            "No nested repositorys available.",
            prefixmanager[0].plain_text())

    def test_manager_is_hided_from_user_without_permission(self):
        self.grant('Contributor')

        self.assertRaises(
            Unauthorized,
            self.browser.open,
            ('%s/referenceprefix_manager' % (self.repo1.absolute_url())))

    def test_unlock_event_gets_logged_in_journal(self):
        self.browser.open('%s/referenceprefix_manager' % (self.repo.absolute_url()))

        # works because we only have one unlock button
        self.browser.getLink("Unlock").click()

        # get last journal entry
        journal = get_journal_entry(self.root, entry=-1)

        self.assertEquals(
            translate(journal.get('action').get('title')),
            'Unlocked prefix %d in %s.' % (1, self.repo.title_or_id()))
