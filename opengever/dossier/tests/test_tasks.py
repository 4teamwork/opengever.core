from datetime import datetime
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.dossier.handlers import reindex_contained_objects
from opengever.dossier.tasks import ReindexDossierTitleTask
from opengever.dossier.tasks import TASK_TYPE
from opengever.testing import IntegrationTestCase
import json
import opengever.dossier.handlers as handlers_mod
import opengever.dossier.tasks as tasks_mod
import transaction


class FakeDescription(object):

    def __init__(self, attributes):
        self.attributes = attributes


class FakeModifiedEvent(object):

    def __init__(self, attributes):
        self.descriptions = [FakeDescription(attributes)]


class TestReindexDossierTitleSubscriber(IntegrationTestCase):
    """Tests for the reindex_contained_objects event subscriber."""

    features = ('bgtasks',)

    def setUp(self):
        super(TestReindexDossierTitleSubscriber, self).setUp()
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
    def test_enqueues_background_task_when_dossier_title_changes(self, browser):
        self.login(self.administrator, browser)
        uid = self.dossier.UID()

        browser.open(self.dossier, view='edit')
        browser.fill({'Title': u'Renamed Dossier'}).save()

        tasks = self._pending_tasks_for(uid)
        self.assertEqual(1, len(tasks))
        args = json.loads(tasks[0].task_arguments)
        self.assertEqual(uid, args[u'uid'])

    @browsing
    def test_enqueues_background_task_when_subdossier_title_changes(self, browser):
        self.login(self.administrator, browser)
        uid = self.subdossier.UID()

        browser.open(self.subdossier, view='edit')
        browser.fill({'Title': u'Renamed Subdossier'}).save()

        tasks = self._pending_tasks_for(uid)
        self.assertEqual(1, len(tasks))
        args = json.loads(tasks[0].task_arguments)
        self.assertEqual(uid, args[u'uid'])

    def test_falls_back_to_synchronous_execution_when_no_admin_unit(self):
        self.login(self.administrator)

        real_get_current_admin_unit = handlers_mod.get_current_admin_unit
        handlers_mod.get_current_admin_unit = lambda: None
        self.addCleanup(
            setattr, handlers_mod, 'get_current_admin_unit', real_get_current_admin_unit)

        real_reindex = handlers_mod.reindex_dossier_title
        calls = []
        handlers_mod.reindex_dossier_title = lambda obj: calls.append(obj)
        self.addCleanup(
            setattr, handlers_mod, 'reindex_dossier_title', real_reindex)

        event = FakeModifiedEvent(['IOpenGeverBase.title'])
        reindex_contained_objects(self.dossier, event)

        self.assertEqual(0, len(self._pending_tasks_for(self.dossier.UID())))
        self.assertEqual([self.dossier], calls)


class TestReindexDossierTitleTask(IntegrationTestCase):
    """Tests for the ReindexDossierTitleTask handler."""

    def setUp(self):
        super(TestReindexDossierTitleTask, self).setUp()
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
        calls = {'dossier': [], 'subdossier': []}
        real_dossier_fn = tasks_mod.reindex_containing_dossier_for_contained_objects
        real_subdossier_fn = tasks_mod.reindex_containing_subdossier_for_contained_objects

        tasks_mod.reindex_containing_dossier_for_contained_objects = (
            lambda obj: calls['dossier'].append(obj))
        tasks_mod.reindex_containing_subdossier_for_contained_objects = (
            lambda obj: calls['subdossier'].append(obj))

        def restore():
            tasks_mod.reindex_containing_dossier_for_contained_objects = real_dossier_fn
            tasks_mod.reindex_containing_subdossier_for_contained_objects = real_subdossier_fn

        self.addCleanup(restore)
        return calls

    def test_execute_dispatches_to_dossier_reindex_for_top_level_dossier(self):
        uid = self.dossier.UID()
        task = self._make_task(uid)
        calls = self._spy_reindex()

        handler = ReindexDossierTitleTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertEqual([self.dossier], calls['dossier'])
        self.assertEqual([], calls['subdossier'])

    def test_execute_dispatches_to_subdossier_reindex_for_subdossier(self):
        uid = self.subdossier.UID()
        task = self._make_task(uid)
        calls = self._spy_reindex()

        handler = ReindexDossierTitleTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertEqual([], calls['dossier'])
        self.assertEqual([self.subdossier], calls['subdossier'])

    def test_execute_skips_missing_object_without_raising(self):
        task = self._make_task(uid=u'nonexistent-uid-0000-0000-000000000000')
        calls = self._spy_reindex()

        handler = ReindexDossierTitleTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertEqual([], calls['dossier'])
        self.assertEqual([], calls['subdossier'])
