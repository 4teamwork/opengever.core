from datetime import datetime
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.repository.tasks import TASK_TYPE
from opengever.repository.tasks import UpdateReferencePrefixesTask
from opengever.testing import IntegrationTestCase
from plone import api
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

    @browsing
    def test_falls_back_to_synchronous_execution_when_no_admin_unit(self, browser):
        self.login(self.administrator, browser)
        uid = self.leaf_repofolder.UID()
        original_unit_id = api.portal.get_registry_record(
            'current_unit_id', interface=IAdminUnitConfiguration)
        api.portal.set_registry_record(
            'current_unit_id', interface=IAdminUnitConfiguration, value=u'')
        self.addCleanup(
            api.portal.set_registry_record,
            'current_unit_id', original_unit_id, interface=IAdminUnitConfiguration)

        import opengever.repository.subscribers as subscribers_mod
        calls = []
        real_reindex = subscribers_mod.reindex_children_with_new_prefix
        subscribers_mod.reindex_children_with_new_prefix = lambda obj: calls.append(obj)
        self.addCleanup(
            setattr, subscribers_mod, 'reindex_children_with_new_prefix', real_reindex)

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Repository number': u'7'}).save()

        self.assertEqual(0, len(self._pending_tasks_for(uid)))
        self.assertEqual(1, len(calls))
        self.assertEqual(self.leaf_repofolder, calls[0])


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
        tasks_mod.reindex_children_with_new_prefix = lambda obj: calls.append(obj)

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
