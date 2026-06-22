from datetime import datetime
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.model import TASK_STATUS_RUNNING
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.bgtasks.task import BaseBackgroundTask
from opengever.bgtasks.task import queue_task
from opengever.bgtasks.task import register_task_type
from opengever.core.testing import MEMORY_DB_LAYER
import transaction
import unittest


class DummyTask(BaseBackgroundTask):
    task_type = u'dummy'

    def execute(self, task, commit_checkpoint):
        pass


register_task_type(u'dummy', DummyTask)


class TestBackgroundTaskModel(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestBackgroundTaskModel, self).setUp()
        self.session = self.layer.session

    def _make_task(self, admin_unit_id=u'unit-1', task_type=u'dummy',
                   status=TASK_STATUS_PENDING, priority=5, scheduled_for=None):
        task = BackgroundTask()
        task.admin_unit_id = admin_unit_id
        task.task_type = task_type
        task.status = status
        task.priority = priority
        task.scheduled_for = scheduled_for
        task.created = datetime.now()
        task.retries = 0
        task.max_retries = 3
        self.session.add(task)
        transaction.commit()
        return task

    def test_queue_task_creates_pending_row(self):
        task = queue_task(u'dummy', u'unit-1', arguments={u'foo': u'bar'})
        transaction.commit()

        self.assertEqual(task.status, TASK_STATUS_PENDING)
        self.assertEqual(task.task_type, u'dummy')
        self.assertEqual(task.admin_unit_id, u'unit-1')
        self.assertEqual(task.priority, 5)
        self.assertIsNone(task.scheduled_for)
        self.assertIsNotNone(task.task_id)
        self.assertIsNotNone(task.created)

    def test_queue_task_stores_arguments_as_json(self):
        task = queue_task(u'dummy', u'unit-1', arguments={u'x': 42})
        transaction.commit()

        from opengever.bgtasks.task import BaseBackgroundTask
        handler = BaseBackgroundTask()
        self.assertEqual(handler.get_arguments(task), {u'x': 42})

    def test_queue_task_with_scheduled_for(self):
        run_at = datetime(2026, 12, 31, 3, 0, 0)
        task = queue_task(u'dummy', u'unit-1', run_at=run_at)
        transaction.commit()

        self.assertEqual(task.scheduled_for, run_at)

    def test_queue_task_raises_for_unknown_type(self):
        with self.assertRaises(ValueError):
            queue_task(u'no-such-type', u'unit-1')

    def test_query_filters_by_admin_unit(self):
        self._make_task(admin_unit_id=u'unit-1')
        self._make_task(admin_unit_id=u'unit-2')

        results = BackgroundTask.query.by_admin_unit(u'unit-1').all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].admin_unit_id, u'unit-1')

    def test_query_pending_returns_only_pending(self):
        self._make_task(admin_unit_id=u'unit-1', status=TASK_STATUS_PENDING)
        self._make_task(admin_unit_id=u'unit-1', status=TASK_STATUS_RUNNING)
        self._make_task(admin_unit_id=u'unit-1', status=TASK_STATUS_SUCCEEDED)

        results = BackgroundTask.query.pending(u'unit-1').all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, TASK_STATUS_PENDING)

    def test_priority_ordering(self):
        self._make_task(admin_unit_id=u'unit-1', priority=10)
        self._make_task(admin_unit_id=u'unit-1', priority=1)
        self._make_task(admin_unit_id=u'unit-1', priority=5)

        session = create_session()
        results = (session.query(BackgroundTask)
                   .filter_by(admin_unit_id=u'unit-1')
                   .order_by(BackgroundTask.priority.asc())
                   .all())

        self.assertEqual([t.priority for t in results], [1, 5, 10])
