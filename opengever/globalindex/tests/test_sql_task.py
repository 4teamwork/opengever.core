from opengever.globalindex.model.task import Task
from opengever.globalindex.testing import MEMORY_DB_LAYER
from opengever.ogds.base.utils import create_session
from sqlalchemy.exc import IntegrityError
from unittest2 import TestCase
import transaction


class TestGlobalindexTask(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestGlobalindexTask, self).setUp()
        self.session = create_session()

    def test_task(self):
        # Create a task.
        t1 = Task(1, 'm1')
        self.session.add(t1)
        # self.assertEquals('<Task 1@m1>', t1.__repr__())

        # Test successors when setting predecessor.
        t2 = Task(2, 'm1')
        self.session.add(t2)
        t2.predecessor = t1
        self.assertEquals(t1, t2.predecessor)

        t3 = Task(3, 'm1')
        self.session.add(t3)
        t3.predecessor = t1
        self.assertEquals(t1, t3.predecessor)
        self.assertEquals([t2, t3], t1.successors)

        transaction.commit()

        # Task IDs must be unique.
        t1 =  Task(1, 'm1')
        self.session.add(t1)

        with self.assertRaises(IntegrityError) as cm:
            transaction.commit()

        expected_msg = '(IntegrityError) columns client_id, int_id are not unique'
        error_msg = str(cm.exception)
        self.assertTrue(
            error_msg.startswith(expected_msg),
            'Expected error message to start with "%s", got "%s"' % (
                expected_msg, error_msg))

        transaction.abort()
