from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import create_session
from opengever.locking.model import Lock
from opengever.meeting.wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import STEALABLE_LOCK
import pytz


class TestLockInfo(IntegrationTestCase):

    lock_message = u'This item was locked by B\xe4rfuss K\xe4thi 1 minute ago.'
    unlock_message = ' If you are certain this user has abandoned the object,'
    unlock_message += ' you may the object. You will then be able to edit it.'

    @browsing
    def test_lockinfo_is_visible_for_lock_owner(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document)
        self.assertEquals([], info_messages())
        lockable = ILockable(self.document)
        lockable.lock()
        browser.open(self.document)
        self.assertEquals([self.lock_message], info_messages())

    @browsing
    def test_unlock_button_is_visible_for_manager(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document)
        self.assertEquals([], info_messages())
        lockable = ILockable(self.document)
        lockable.lock()
        self.login(self.manager, browser=browser)
        browser.open(self.document)
        self.assertEquals([self.lock_message + self.unlock_message], info_messages())


class TestSQLLockable(FunctionalTestCase):

    def setUp(self):
        super(TestSQLLockable, self).setUp()
        self.session = create_session()
        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .with_default_period()
                                .within(self.container))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee.load_model()))

        self.wrapper = MeetingWrapper.wrap(self.committee, self.meeting)

    def test_lock_use_model_class_name_as_object_type(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        lock = Lock.query.first()
        self.assertEqual(u'Meeting', lock.object_type)

    def test_lock_token_contains_object_type_and_is_separated_with_a_colon(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        lock = Lock.query.first()
        self.assertEqual(u'Meeting:1', lock.token)

    def test_locked(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()
        self.assertTrue(lockable.locked())

    def test_refresh_locks_update_locks_to_current_time(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        with freeze(pytz.UTC.localize(datetime(2015, 03, 10, 12, 05))):
            lockable.refresh_lock()

            lock = Lock.query.one()
            self.assertEqual(
                pytz.UTC.localize(datetime(2015, 03, 10, 12, 05)), lock.time)

    def test_unlock_does_nothing_for_not_locked_items(self):
        lockable = ILockable(self.wrapper)
        lockable.unlock()

    def test_unlock_delete_lock_if_a_lock_existsts(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()
        lockable.unlock()
        self.assertFalse(lockable.locked())
        self.assertEquals(0, Lock.query.count())

    def test_unlock_does_not_check_if_lock_is_stealable_when_stealable_only_is_false(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        # manually change lock creator
        lock = Lock.query.first()
        lock.creator = 'other-user'

        lockable.unlock()
        self.assertFalse(lockable.locked())

    def test_clear_locks_remove_all_locks_on_the_object(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()
        self.assertTrue(lockable.locked())

        lockable.clear_locks()
        self.assertFalse(lockable.locked())

    def test_locked_is_true_if_a_valid_lock_exists(self):
        create(Builder('lock')
               .of_obj(self.wrapper)
               .having(time=utcnow_tz_aware() - timedelta(seconds=100)))
        lockable = ILockable(self.wrapper)
        self.assertTrue(lockable.locked())

    def test_locked_is_false_if_lock_is_invalid(self):
        create(Builder('lock')
               .of_obj(self.wrapper)
               .having(time=utcnow_tz_aware() - timedelta(seconds=800)))

        lockable = ILockable(self.wrapper)
        self.assertFalse(lockable.locked())

    def test_locked_is_false_if_no_lock_exists(self):
        lockable = ILockable(self.wrapper)
        self.assertFalse(lockable.locked())

    def test_can_safely_unlock_is_true_if_no_lock_exists(self):
        lockable = ILockable(self.wrapper)
        self.assertTrue(lockable.can_safely_unlock())

    def test_can_safely_unlock_is_true_if_a_lock_of_the_current_user_exists(self):
        create(Builder('lock')
               .of_obj(self.wrapper)
               .having(lock_type=u'plone.locking.stealable'))

        self.assertTrue(ILockable(self.wrapper).can_safely_unlock())

    def test_can_safely_unlock_is_false_if_item_is_locked_by_an_other_user(self):
        create(Builder('lock')
               .of_obj(self.wrapper)
               .having(creator=u'hugo.boss'))

        self.assertFalse(ILockable(self.wrapper).can_safely_unlock())

    def test_lock_info_returns_an_list_of_dicts_of_all_valid_locks(self):
        # valid
        lock1 = create(Builder('lock')
                       .of_obj(self.wrapper)
                       .having(time=utcnow_tz_aware() - timedelta(seconds=100)))

        self.assertEquals(
            [{'creator': TEST_USER_ID,
              'time': lock1.time,
              'token': 'Meeting:1',
              'type': STEALABLE_LOCK}],
            ILockable(self.wrapper).lock_info())

        # invalid
        lock1.time = utcnow_tz_aware() - timedelta(seconds=800)
        self.assertEquals([], ILockable(self.wrapper).lock_info())

    def test_during_lock_creation_the_expired_locks_gets_cleared(self):
        lock_1 = create(Builder('lock')
                        .having(object_type='Meeting',
                                object_id=12345,
                                time=utcnow_tz_aware() - timedelta(seconds=1000)))

        lock_2 = create(Builder('lock')
                        .having(object_type='Meeting',
                                object_id=56789,
                                time=utcnow_tz_aware() - timedelta(seconds=800)))

        ILockable(self.wrapper).lock()

        locks = Lock.query.all()

        self.assertEquals(1, len(locks))
        self.assertNotIn(lock_1, locks)
        self.assertNotIn(lock_2, locks)

    def test_lock_creation_removes_expired_locks_for_same_object(self):
        expired_lock = create(
            Builder('lock')
            .of_obj(self.wrapper)
            .having(time=utcnow_tz_aware() - timedelta(seconds=1000)))

        ILockable(self.wrapper).lock()

        locks = Lock.query.all()
        self.assertEquals(1, len(locks))
        self.assertNotIn(expired_lock, locks)
