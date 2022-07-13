from DateTime import DateTime
from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.journal.manager import AutoEntryManipulationException
from opengever.journal.manager import JournalManager
from opengever.testing import IntegrationTestCase
from zope.i18n import translate
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
            zope_time = DateTime()
            manager.add_manual_entry('information', 'is an agent')

        self.assertEqual(1, manager.count())
        entry = manager.list().pop()
        self.assertEqual(u'is an agent', entry.get('comments'))
        self.assertEqual(zope_time, entry.get('time'))

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

    @browsing
    def test_can_modify_entry(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            zope_time = DateTime()
            manager.add_manual_entry('information', 'is an agent')

        entry = manager.list()[0]
        self.assertEqual(u'is an agent', entry.get('comments'))
        self.assertEqual(u'information', entry.get('action').get('category'))
        self.assertEqual(u'Manual entry: Information', translate(entry.get('action').get('title')))
        self.assertEqual([], entry.get('action').get('documents'))
        self.assertEqual(zope_time, entry.get('time'))

        manager.update(entry.get('id'), comment='my new comment', category='phone-call', documents=[self.document])
        entry = manager.list()[0]

        self.assertEqual(u'my new comment', entry.get('comments'))
        self.assertEqual(u'phone-call', entry.get('action').get('category'))
        self.assertEqual(u'Manual entry: Phone call', translate(entry.get('action').get('title')))
        self.assertEqual([{'id': u'plone:1014073300', 'title': u'Vertr\xe4gsentwurf'}], entry.get('action').get('documents'))
        self.assertEqual(zope_time, entry.get('time'))

    @browsing
    def test_modify_invalid_entry_will_raise(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with self.assertRaises(KeyError):
            manager.update('invalid', comment='my new comment')

    @browsing
    def test_only_manual_entries_can_be_modified(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)

        with self.assertRaises(AutoEntryManipulationException):
            manager.update(manager.list()[0].get('id'), comment='my new comment')

    @browsing
    def test_add_validates_time(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with self.assertRaises(ValueError) as cm:
            manager.add_manual_entry('information', 'is an agent',
                                     time="2022-07-13 12:57:30")

        self.assertEqual(
            "time should be a zope DateTime not <type 'str'>",
            str(cm.exception))

        self.assertEqual(0, manager.count())

        with self.assertRaises(ValueError) as cm:
            manager.add_manual_entry('information', 'is an agent',
                                     time=datetime.now())

        self.assertEqual(0, manager.count())
        self.assertEqual(
            "time should be a zope DateTime not <type 'datetime.datetime'>",
            str(cm.exception))

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            zope_time = DateTime()
            manager.add_manual_entry('information', 'is an agent',
                                     time=DateTime())

        self.assertEqual(1, manager.count())
        entry = manager.list()[0]
        self.assertEqual(u'is an agent', entry.get('comments'))
        self.assertEqual(zope_time, entry.get('time'))

    @browsing
    def test_modify_validates_time(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            zope_time = DateTime()
            manager.add_manual_entry('information', 'is an agent')

        entry = manager.list()[0]
        self.assertEqual(u'is an agent', entry.get('comments'))
        self.assertEqual(zope_time, entry.get('time'))

        with self.assertRaises(ValueError) as cm:
            manager.update(entry.get('id'), time=datetime.now())

        self.assertEqual(
            "time should be a zope DateTime not <type 'datetime.datetime'>",
            str(cm.exception))

        with freeze(datetime(2018, 12, 14, 0, 0, tzinfo=pytz.utc)):
            new_zope_time = DateTime()
            manager.update(entry.get('id'), time=DateTime())

        entry = manager.list()[0]
        self.assertEqual(u'is an agent', entry.get('comments'))
        self.assertEqual(new_zope_time, entry.get('time'))
