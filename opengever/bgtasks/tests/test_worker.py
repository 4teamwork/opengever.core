from datetime import datetime
from datetime import timedelta
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_FAILED
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.model import TASK_STATUS_RUNNING
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.bgtasks.task import BaseBackgroundTask
from opengever.bgtasks.task import register_task_type
from opengever.bgtasks.worker import BackgroundTaskWorker
from opengever.core.testing import MEMORY_DB_LAYER
import json
import logging
import transaction
import unittest


class SucceedingTask(BaseBackgroundTask):
    task_type = u'succeeding'

    def execute(self, task, commit_checkpoint):
        pass


class FailingTask(BaseBackgroundTask):
    task_type = u'failing'

    def execute(self, task, commit_checkpoint):
        raise RuntimeError(u'boom')


class CheckpointingTask(BaseBackgroundTask):
    task_type = u'checkpointing'

    def execute(self, task, commit_checkpoint):
        commit_checkpoint({u'step': 1, u'done': True})


register_task_type(u'succeeding', SucceedingTask)
register_task_type(u'failing', FailingTask)
register_task_type(u'checkpointing', CheckpointingTask)


class TestBackgroundTaskWorker(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestBackgroundTaskWorker, self).setUp()
        self.session = self.layer.session
        self.worker = BackgroundTaskWorker(log=logging.getLogger('test'))

    def _make_task(self, admin_unit_id=u'unit-1', task_type=u'succeeding',
                   status=TASK_STATUS_PENDING, priority=5, scheduled_for=None,
                   retries=0, max_retries=3):
        task = BackgroundTask()
        task.task_id = u'task-%s' % id(task)
        task.admin_unit_id = admin_unit_id
        task.task_type = task_type
        task.status = status
        task.priority = priority
        task.scheduled_for = scheduled_for
        task.created = datetime.now()
        task.retries = retries
        task.max_retries = max_retries
        self.session.add(task)
        transaction.commit()
        return task

    def test_reset_interrupted_tasks_resets_running_to_pending(self):
        task = self._make_task(status=TASK_STATUS_RUNNING)
        task.started = datetime.now()
        transaction.commit()

        self.worker.reset_interrupted_tasks(u'unit-1')

        self.assertEqual(task.status, TASK_STATUS_PENDING)
        self.assertIsNone(task.started)

    def test_reset_interrupted_tasks_preserves_checkpoint_data(self):
        task = self._make_task(status=TASK_STATUS_RUNNING)
        task.checkpoint_data = json.dumps({u'step': 5})
        transaction.commit()

        self.worker.reset_interrupted_tasks(u'unit-1')

        self.assertEqual(task.status, TASK_STATUS_PENDING)
        self.assertIsNotNone(task.checkpoint_data)

    def test_reset_interrupted_does_not_touch_other_admin_units(self):
        task = self._make_task(admin_unit_id=u'unit-2', status=TASK_STATUS_RUNNING)

        self.worker.reset_interrupted_tasks(u'unit-1')

        self.assertEqual(task.status, TASK_STATUS_RUNNING)

    def test_claim_next_task_returns_pending_task(self):
        task = self._make_task(status=TASK_STATUS_PENDING)

        claimed = self.worker.claim_next_task(u'unit-1')

        self.assertEqual(claimed.task_id, task.task_id)

    def test_claim_next_task_respects_priority(self):
        low = self._make_task(priority=10)
        high = self._make_task(priority=1)

        claimed = self.worker.claim_next_task(u'unit-1')

        self.assertEqual(claimed.task_id, high.task_id)

    def test_claim_next_task_skips_future_scheduled_tasks(self):
        future = datetime.now() + timedelta(hours=1)
        self._make_task(scheduled_for=future)

        claimed = self.worker.claim_next_task(u'unit-1')

        self.assertIsNone(claimed)

    def test_claim_next_task_includes_past_scheduled_tasks(self):
        past = datetime.now() - timedelta(hours=1)
        task = self._make_task(scheduled_for=past)

        claimed = self.worker.claim_next_task(u'unit-1')

        self.assertEqual(claimed.task_id, task.task_id)

    def test_claim_next_task_returns_none_when_queue_empty(self):
        claimed = self.worker.claim_next_task(u'unit-1')

        self.assertIsNone(claimed)

    def test_claim_next_task_ignores_other_admin_units(self):
        self._make_task(admin_unit_id=u'unit-2', status=TASK_STATUS_PENDING)

        claimed = self.worker.claim_next_task(u'unit-1')

        self.assertIsNone(claimed)

    def test_execute_task_marks_succeeded_on_success(self):
        task = self._make_task(task_type=u'succeeding')

        self.worker.execute_task(task)

        self.assertEqual(task.status, TASK_STATUS_SUCCEEDED)
        self.assertIsNotNone(task.finished)

    def test_execute_task_requeues_on_failure_when_retries_left(self):
        task = self._make_task(task_type=u'failing', retries=0, max_retries=3)

        self.worker.execute_task(task)

        self.assertEqual(task.status, TASK_STATUS_PENDING)
        self.assertEqual(task.retries, 1)
        self.assertIsNotNone(task.error_message)

    def test_execute_task_marks_failed_when_retries_exhausted(self):
        task = self._make_task(task_type=u'failing', retries=3, max_retries=3)

        self.worker.execute_task(task)

        self.assertEqual(task.status, TASK_STATUS_FAILED)
        self.assertEqual(task.retries, 4)
        self.assertIsNotNone(task.finished)

    def test_commit_checkpoint_persists_data(self):
        task = self._make_task(task_type=u'checkpointing')

        self.worker.execute_task(task)

        self.assertEqual(task.status, TASK_STATUS_SUCCEEDED)
        stored = json.loads(task.checkpoint_data)
        self.assertEqual(stored, {u'step': 1, u'done': True})

    def test_checkpoint_data_survives_restart(self):
        task = self._make_task(status=TASK_STATUS_RUNNING)
        task.checkpoint_data = json.dumps({u'progress': 42})
        transaction.commit()

        self.worker.reset_interrupted_tasks(u'unit-1')

        self.assertEqual(task.status, TASK_STATUS_PENDING)
        resumed = json.loads(task.checkpoint_data)
        self.assertEqual(resumed[u'progress'], 42)
