from mock import patch
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.task import BaseBackgroundTask
from opengever.bgtasks.task import queue_task
from opengever.bgtasks.task import register_task_type
from opengever.core.testing import MEMORY_DB_LAYER
import transaction
import unittest


class RecordingTask(BaseBackgroundTask):
    task_type = u'recording'
    calls = []

    def execute(self, task, commit_checkpoint):
        commit_checkpoint({u'checkpointed': True})
        self.calls.append(self.get_arguments(task))


register_task_type(u'recording', RecordingTask)


class TestQueueTaskFlag(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestQueueTaskFlag, self).setUp()
        self.session = self.layer.session
        RecordingTask.calls = []

    def _pending_rows(self, task_type=u'recording'):
        return (self.session.query(BackgroundTask)
                .filter_by(task_type=task_type)
                .all())

    @patch('opengever.bgtasks.task.is_background_tasks_enabled', return_value=True)
    def test_enabled_creates_pending_row_and_does_not_execute(self, mocked_enabled):
        task = queue_task(u'recording', u'unit-1', arguments={u'x': 1})
        transaction.commit()

        self.assertEqual(1, len(self._pending_rows()))
        self.assertEqual(task.status, u'pending')
        self.assertEqual([], RecordingTask.calls)

    @patch('opengever.bgtasks.task.is_background_tasks_enabled', return_value=False)
    def test_disabled_executes_synchronously_and_creates_no_row(self, mocked_enabled):
        task = queue_task(u'recording', u'unit-1', arguments={u'x': 2})
        transaction.commit()

        self.assertEqual(0, len(self._pending_rows()))
        self.assertEqual([{u'x': 2}], RecordingTask.calls)
        self.assertEqual(u'unit-1', task.admin_unit_id)
        self.assertIsNotNone(task.task_id)

    def test_unreadable_registry_defaults_to_disabled(self):
        # No Plone site in this layer, so the registry read itself fails,
        # exercising the real is_background_tasks_enabled() fail-safe path.
        queue_task(u'recording', u'unit-1', arguments={u'x': 3})
        transaction.commit()

        self.assertEqual(0, len(self._pending_rows()))
        self.assertEqual([{u'x': 3}], RecordingTask.calls)

    @patch('opengever.bgtasks.task.is_background_tasks_enabled', return_value=True)
    def test_unknown_task_type_raises_when_enabled(self, mocked_enabled):
        with self.assertRaises(ValueError):
            queue_task(u'no-such-type', u'unit-1')

    @patch('opengever.bgtasks.task.is_background_tasks_enabled', return_value=False)
    def test_unknown_task_type_raises_when_disabled(self, mocked_enabled):
        with self.assertRaises(ValueError):
            queue_task(u'no-such-type', u'unit-1')
