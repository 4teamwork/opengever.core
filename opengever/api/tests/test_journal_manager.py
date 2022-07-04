from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.journal.manager import AutoEntryManipulationException
from opengever.journal.manager import JournalManager
from opengever.testing import IntegrationTestCase
import pytz


class TestJournalManager(IntegrationTestCase):

    @browsing
    def test_can_count_entries(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        self.assertEqual(0, manager.count())
        manager.add_manual_entry('information', 'first')
        self.assertEqual(1, manager.count())

    @browsing
    def test_can_clear_entries(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)

        self.assertEqual(17, manager.count())

        manager.clear()

        self.assertEqual(0, manager.count())

    @browsing
    def test_can_list_entries(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)

        manager.clear()

        manager.add_manual_entry('information', 'first')
        manager.add_manual_entry('information', 'second')

        entry_comments = [item.get('comments') for item in manager.list()]
        self.assertEqual(['first', 'second'], entry_comments)

    @browsing
    def test_can_add_manual_entries(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            manager.add_manual_entry('information', 'is an agent')

        self.assertEqual(1, manager.count())
        self.assertEqual(u'is an agent', manager.list().pop().get('comments'))

    @browsing
    def test_can_add_auto_entries(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            manager.add_auto_entry('dossier modified', 'Dossier modified')

        self.assertEqual(1, manager.count())
        self.assertEqual(u'Dossier modified', manager.list().pop().get('action').get('title'))

    @browsing
    def test_can_lookup_entries(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'is an agent')
        entry_id = manager.list()[0].get('id')
        entry = manager.lookup(entry_id)
        self.assertEqual(u'is an agent', entry.get('comments'))

    @browsing
    def test_lookup_invalid_entry_will_raise(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with self.assertRaises(KeyError):
            manager.lookup('invalid')

    @browsing
    def test_can_remove_entries(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'my comment')
        entry_id = manager.list()[0].get('id')

        self.assertEqual(1, manager.count())
        manager.remove(entry_id)
        self.assertEqual(0, manager.count())

    @browsing
    def test_remove_invalid_entry_will_raise(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with self.assertRaises(KeyError):
            manager.remove('invalid')

    @browsing
    def test_remove_auto_entry_will_raise(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)

        with self.assertRaises(AutoEntryManipulationException):
            manager.remove(manager.list()[0].get('id'))
