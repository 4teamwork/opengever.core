from opengever.testing import IntegrationTestCase
from opengever.wopi.lock import create_lock
from opengever.wopi.lock import get_lock_token
from opengever.wopi.lock import refresh_lock
from opengever.wopi.lock import unlock
from plone.locking.interfaces import ILockable


class TestLocking(IntegrationTestCase):

    def test_create_lock_locks_document(self):
        self.login(self.regular_user)
        create_lock(self.document, 'LOCK-TOKEN')
        self.assertTrue(self.document.is_locked())

    def test_get_lock_token_for_locked_object_returns_token(self):
        self.login(self.regular_user)
        create_lock(self.document, 'LOCK-TOKEN')
        self.assertEqual(get_lock_token(self.document), 'LOCK-TOKEN')

    def test_get_lock_token_for_unlocked_object_returns_none(self):
        self.login(self.regular_user)
        self.assertEqual(get_lock_token(self.document), None)

    def test_get_lock_token_for_object_with_other_lock_returns_none(self):
        self.login(self.regular_user)
        lockable = ILockable(self.document)
        lockable.lock()
        self.assertEqual(get_lock_token(self.document), None)

    def test_unlock_document(self):
        self.login(self.regular_user)
        create_lock(self.document, 'LOCK-TOKEN')
        self.assertTrue(self.document.is_locked())
        unlock(self.document)
        self.assertFalse(self.document.is_locked())

    def test_refresh_lock(self):
        self.login(self.regular_user)
        create_lock(self.document, 'LOCK-TOKEN')
        mtime = self.document.wl_lockItems()[0][1].getModifiedTime()
        refresh_lock(self.document)
        self.assertGreater(
            self.document.wl_lockItems()[0][1].getModifiedTime(), mtime)
