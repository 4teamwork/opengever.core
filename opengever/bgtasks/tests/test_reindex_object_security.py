from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.reindex_object_security import ReindexObjectSecurityTask
from opengever.bgtasks.reindex_object_security import TASK_TYPE
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.testing import IntegrationTestCase
from plone import api
import json
import transaction


class TestReindexObjectSecurityPatch(IntegrationTestCase):
    """Tests for PatchCMFCatalogAwareReindexObjectSecurity."""

    features = ('bgtasks',)

    def setUp(self):
        super(TestReindexObjectSecurityPatch, self).setUp()
        self.login(self.regular_user)
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

    def test_enqueues_background_task_on_reindex_object_security(self):
        uid = self.dossier.UID()
        self.dossier.reindexObjectSecurity()

        tasks = self._pending_tasks_for(uid)
        self.assertEqual(1, len(tasks))
        args = json.loads(tasks[0].task_arguments)
        self.assertEqual(uid, args[u'uid'])
        self.assertFalse(args[u'skip_self'])

    def test_deduplication_replaces_existing_pending_task(self):
        uid = self.dossier.UID()
        self.dossier.reindexObjectSecurity()
        transaction.commit()

        first_task_id = self._pending_tasks_for(uid)[0].task_id
        self.dossier.reindexObjectSecurity()

        tasks = self._pending_tasks_for(uid)
        self.assertEqual(1, len(tasks))
        self.assertNotEqual(first_task_id, tasks[0].task_id)

    def test_skip_self_stored_in_task_arguments(self):
        uid = self.dossier.UID()
        self.dossier.reindexObjectSecurity(skip_self=True)

        tasks = self._pending_tasks_for(uid)
        self.assertEqual(1, len(tasks))
        args = json.loads(tasks[0].task_arguments)
        self.assertTrue(args[u'skip_self'])

    def test_falls_through_to_original_when_no_admin_unit(self):
        uid = self.dossier.UID()
        api.portal.set_registry_record(
            'current_unit_id', interface=IAdminUnitConfiguration, value=u'')

        import opengever.bgtasks.patches as _patches_mod
        original_called = []

        real_original = _patches_mod._original_reindex_object_security

        def spy_original(self_obj, skip_self=False):
            original_called.append((self_obj, skip_self))
            return real_original(self_obj, skip_self=skip_self)

        _patches_mod._original_reindex_object_security = spy_original
        try:
            self.dossier.reindexObjectSecurity()
        finally:
            _patches_mod._original_reindex_object_security = real_original

        self.assertEqual(1, len(original_called))
        self.assertEqual(0, len(self._pending_tasks_for(uid)))


class TestReindexObjectSecurityTask(IntegrationTestCase):
    """Tests for ReindexObjectSecurityTask handler."""

    def setUp(self):
        super(TestReindexObjectSecurityTask, self).setUp()
        self.login(self.regular_user)

    def _make_task(self, uid, skip_self=False):
        task = BackgroundTask()
        task.admin_unit_id = u'plone'
        task.task_type = TASK_TYPE
        task.status = TASK_STATUS_PENDING
        task.priority = 5
        task.task_arguments = json.dumps({u'uid': uid, u'skip_self': skip_self})
        from datetime import datetime
        task.created = datetime.now()
        task.retries = 0
        task.max_retries = 3
        create_session().add(task)
        transaction.commit()
        return task

    def _no_op_commit_checkpoint(self, data):
        pass

    def test_execute_calls_original_reindex_for_existing_object(self):
        uid = self.dossier.UID()
        task = self._make_task(uid)

        import opengever.bgtasks.patches as _patches_mod
        real_original = _patches_mod._original_reindex_object_security
        calls = []

        def spy_original(obj, skip_self=False):
            calls.append((obj, skip_self))

        _patches_mod._original_reindex_object_security = spy_original
        try:
            handler = ReindexObjectSecurityTask()
            handler.execute(task, self._no_op_commit_checkpoint)
        finally:
            _patches_mod._original_reindex_object_security = real_original

        self.assertEqual(1, len(calls))
        self.assertEqual(self.dossier, calls[0][0])
        self.assertFalse(calls[0][1])

    def test_execute_passes_skip_self_to_original(self):
        uid = self.dossier.UID()
        task = self._make_task(uid, skip_self=True)

        import opengever.bgtasks.patches as _patches_mod
        real_original = _patches_mod._original_reindex_object_security
        calls = []

        def spy_original(obj, skip_self=False):
            calls.append(skip_self)

        _patches_mod._original_reindex_object_security = spy_original
        try:
            handler = ReindexObjectSecurityTask()
            handler.execute(task, self._no_op_commit_checkpoint)
        finally:
            _patches_mod._original_reindex_object_security = real_original

        self.assertEqual([True], calls)

    def test_execute_skips_missing_object_without_raising(self):
        task = self._make_task(uid=u'nonexistent-uid-0000-0000-000000000000')

        import opengever.bgtasks.patches as _patches_mod
        real_original = _patches_mod._original_reindex_object_security
        calls = []

        _patches_mod._original_reindex_object_security = lambda obj, skip_self=False: calls.append(obj)
        try:
            handler = ReindexObjectSecurityTask()
            handler.execute(task, self._no_op_commit_checkpoint)
        finally:
            _patches_mod._original_reindex_object_security = real_original

        self.assertEqual(0, len(calls))
