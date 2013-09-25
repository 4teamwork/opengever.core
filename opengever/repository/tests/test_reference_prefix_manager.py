from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.base.adapters import ReferenceNumberPrefixAdpater
import transaction


class TestReferencePrefixManager(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestReferencePrefixManager, self).setUp()
        self.grant('Contributor')

        self.root = create(Builder('repository').titled('Weiterbildung'))
        self.repo1 = create(Builder('repository')
                        .titled("One")
                        .within(self.root))
        self.repo2 = create(Builder('repository')
                        .titled("Two")
                        .within(self.root))

        self.refs = ReferenceNumberPrefixAdpater(self.root)
        # move repo1 to prefix 3 which leaves prefix 1 unused
        self.refs.set_number(self.repo1, 3)
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
        self.browser.open('%s/referenceprefix_manager' % (self.root.absolute_url()))
        table = self.parse_manager_table_data()

        self.assertEquals([
                ['1', 'One', 'Unlock'],
                ['2', 'Two', 'In use'],
                ['3', 'One', 'In use']
            ], table)

    def test_manager_deletes_unused_prefix_when_button_is_clicked(self):
        self.browser.open('%s/referenceprefix_manager' % (self.root.absolute_url()))

        self.browser.getLink("Unlock").click()

        table = self.parse_manager_table_data()

        self.assertEquals([
            ['2', 'Two', 'In use'],
            ['3', 'One', 'In use']
        ], table)

    def test_manager_throws_error_when_delete_request_for_used_prefix_occurs(self):
        self.assertRaises(Exception, self.refs.free_number, (2))

    def test_manager_shows_default_message_when_no_repositorys_available(self):
        self.browser.open('%s/referenceprefix_manager' % (self.repo1.absolute_url()))

        prefixmanager = self.browser.css("#content")

        self.assertIn(
            "No nested repositorys available.",
            prefixmanager[0].plain_text()
        )

    def test_manager_is_hided_from_user_without_permission(self):
        pass # TODO
