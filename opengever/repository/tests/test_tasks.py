from datetime import datetime
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.repository.tasks import TASK_TYPE
from opengever.repository.tasks import UpdateReferencePrefixesTask
from opengever.testing import IntegrationTestCase
import json
import transaction


class TestUpdateReferencePrefixesSubscriber(IntegrationTestCase):
    """Tests for the update_reference_prefixes event subscriber."""

    features = ('bgtasks',)

    def setUp(self):
        super(TestUpdateReferencePrefixesSubscriber, self).setUp()
        self._clear_queue()

    def _clear_queue(self):
        session = create_session()
        session.query(BackgroundTask).delete()
        transaction.commit()

    def _pending_tasks_for(self, uid):
        session = create_session()
        tasks = (session.query(BackgroundTask)
                 .filter_by(task_type=TASK_TYPE,
                            status=TASK_STATUS_PENDING)
                 .all())
        return [t for t in tasks
                if json.loads(t.task_arguments or u'{}').get(u'uid') == uid]

    @browsing
    def test_enqueues_background_task_when_prefix_changes(self, browser):
        self.login(self.administrator, browser)
        uid = self.leaf_repofolder.UID()

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Repository number': u'7'}).save()

        tasks = self._pending_tasks_for(uid)
        self.assertEqual(1, len(tasks))
        args = json.loads(tasks[0].task_arguments)
        self.assertEqual(uid, args[u'uid'])


class TestUpdateReferencePrefixesTask(IntegrationTestCase):
    """Tests for the UpdateReferencePrefixesTask handler."""

    def setUp(self):
        super(TestUpdateReferencePrefixesTask, self).setUp()
        self.login(self.administrator)

    def _make_task(self, uid):
        task = BackgroundTask()
        task.admin_unit_id = u'plone'
        task.task_type = TASK_TYPE
        task.status = TASK_STATUS_PENDING
        task.priority = 5
        task.task_arguments = json.dumps({u'uid': uid})
        task.created = datetime.now()
        task.retries = 0
        task.max_retries = 3
        create_session().add(task)
        transaction.commit()
        return task

    def _no_op_commit_checkpoint(self, data):
        pass

    def _spy_reindex(self):
        import opengever.repository.tasks as tasks_mod
        calls = []
        real_reindex = tasks_mod.reindex_children_with_new_prefix
        tasks_mod.reindex_children_with_new_prefix = lambda obj, **kw: calls.append(obj)

        def restore():
            tasks_mod.reindex_children_with_new_prefix = real_reindex

        self.addCleanup(restore)
        return calls

    def test_execute_reindexes_resolved_object(self):
        uid = self.leaf_repofolder.UID()
        task = self._make_task(uid)
        calls = self._spy_reindex()

        handler = UpdateReferencePrefixesTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertEqual(1, len(calls))
        self.assertEqual(self.leaf_repofolder, calls[0])

    def test_execute_skips_missing_object_without_raising(self):
        task = self._make_task(uid=u'nonexistent-uid-0000-0000-000000000000')
        calls = self._spy_reindex()

        handler = UpdateReferencePrefixesTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertEqual(0, len(calls))

    def _patch_checkpoint_interval(self, value):
        import opengever.repository.tasks as tasks_mod
        original = tasks_mod.CHECKPOINT_INTERVAL
        tasks_mod.CHECKPOINT_INTERVAL = value
        self.addCleanup(setattr, tasks_mod, 'CHECKPOINT_INTERVAL', original)

    def test_execute_commits_checkpoint_every_n_objects(self):
        self._patch_checkpoint_interval(2)
        task = self._make_task(self.repository_root.UID())

        checkpoints = []

        def commit_checkpoint(data, processed, total=None):
            checkpoints.append(data)
        UpdateReferencePrefixesTask().execute(task, commit_checkpoint)

        self.assertGreater(len(checkpoints), 0)
        paths = [cp[u'last_path'] for cp in checkpoints]
        self.assertEqual(len(paths), len(set(paths)))

    def test_execute_resumes_after_last_checkpointed_path(self):
        self._patch_checkpoint_interval(2)
        task = self._make_task(self.repository_root.UID())

        first_run = []

        def first_run_checkpoint(data, processed, total=None):
            first_run.append(data)
        UpdateReferencePrefixesTask().execute(task, first_run_checkpoint)
        self.assertGreater(len(first_run), 1)

        task.checkpoint_data = json.dumps(first_run[0])

        second_run = []

        def second_run_checkpoint(data, processed, total=None):
            second_run.append(data)
        UpdateReferencePrefixesTask().execute(task, second_run_checkpoint)

        self.assertEqual(first_run[1:], second_run)
