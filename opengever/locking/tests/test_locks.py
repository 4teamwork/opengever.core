from datetime import timedelta
from opengever.base.date_time import utcnow_tz_aware
from opengever.core.testing import MEMORY_DB_LAYER
from opengever.locking.model import Lock
from plone.app.testing import TEST_USER_ID
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
import transaction


class TestUnitLocks(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitLocks, self).setUp()
        self.session = self.layer.session

    def test_valid_locks_query(self):
        valid = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=300))
        self.session.add(valid)

        invalid = Lock(object_type='Meeting',
                       object_id=2,
                       creator=TEST_USER_ID,
                       time=utcnow_tz_aware() - timedelta(seconds=800))
        self.session.add(invalid)

        query = Lock.query.valid_locks('Meeting', 1)
        self.assertEquals([valid], query.all())

    def test_is_valid(self):
        lock1 = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=300))
        self.session.add(lock1)

        lock2 = Lock(object_type='Meeting',
                     object_id=2,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=800))
        self.session.add(lock2)


        self.assertTrue(lock1.is_valid())
        self.assertFalse(lock2.is_valid())

    def test_unique_constraint_on_type_id_and_locktype(self):
        lock1 = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     lock_type=u'plone.locking.stealable',
                     time=utcnow_tz_aware() - timedelta(seconds=300))
        self.session.add(lock1)

        with self.assertRaises(IntegrityError):
            lock2 = Lock(object_type='Meeting',
                         object_id=1,
                         creator=TEST_USER_ID,
                         lock_type=u'plone.locking.stealable',
                         time=utcnow_tz_aware())
            self.session.add(lock2)
            transaction.commit()

        transaction.abort()
