from AccessControl import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager
from datetime import datetime
from ftw.testbrowser import browsing
from OFS.CopySupport import CopyError
from OFS.CopySupport import ResourceLockedError
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.move import MoveObjectsTask
from opengever.bgtasks.move import TASK_TYPE
from opengever.dossier.tests.test_move_items import MoveItemsHelper
from opengever.locking.lock import MOVE_LOCK
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.testing import IntegrationTestCase
from plone import api
from plone.locking.interfaces import ILockable
import json
import transaction


class TestMoveObjectsEnqueue(IntegrationTestCase, MoveItemsHelper):
    """Tests for enqueueing `move-objects` tasks from the `@move` REST
    endpoint and the classic `MoveItemsForm`.
    """

    features = ('bgtasks',)

    def setUp(self):
        super(TestMoveObjectsEnqueue, self).setUp()
        self._clear_queue()

    def _clear_queue(self):
        session = create_session()
        session.query(BackgroundTask).delete()
        transaction.commit()

    def _pending_tasks(self):
        session = create_session()
        return (session.query(BackgroundTask)
                .filter_by(task_type=TASK_TYPE, status=TASK_STATUS_PENDING)
                .all())

    @browsing
    def test_api_move_queues_task_with_destination_uid_clipboard_and_user(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.subdossier,
            view='@move',
            data=json.dumps({'source': self.document.absolute_url()}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(202, browser.status_code)
        tasks = self._pending_tasks()
        self.assertEqual(1, len(tasks))
        args = json.loads(tasks[0].task_arguments)
        self.assertEqual(self.subdossier.UID(), args[u'destination_uid'])
        self.assertEqual(self.regular_user.getId(), args[u'user_id'])
        self.assertIn(u'clipboard', args)

    def test_move_items_form_queues_one_task_per_item(self):
        self.login(self.regular_user)
        self.move_items([self.subdocument, self.subsubdossier],
                        source=self.subdossier,
                        target=self.empty_dossier)

        tasks = self._pending_tasks()
        self.assertEqual(2, len(tasks))
        for task in tasks:
            args = json.loads(task.task_arguments)
            self.assertEqual(self.empty_dossier.UID(), args[u'destination_uid'])
            self.assertEqual(self.regular_user.getId(), args[u'user_id'])

    def test_falls_back_to_synchronous_paste_when_no_admin_unit(self):
        self.login(self.regular_user)
        api.portal.set_registry_record(
            'current_unit_id', interface=IAdminUnitConfiguration, value=u'')

        with self.observe_children(self.empty_dossier) as children:
            self.move_items([self.subdocument],
                            source=self.subdossier,
                            target=self.empty_dossier)

        self.assertEqual(0, len(self._pending_tasks()))
        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        self.assertFalse(ILockable(moved).locked())

    @browsing
    def test_api_move_locks_the_object_before_queuing_the_task(self, browser):
        self.login(self.regular_user, browser)
        self.assertFalse(ILockable(self.document).locked())

        browser.open(
            self.subdossier,
            view='@move',
            data=json.dumps({'source': self.document.absolute_url()}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(202, browser.status_code)
        self.assertEqual(1, len(self._pending_tasks()))
        self.assertTrue(ILockable(self.document).locked())

    def test_move_items_form_locks_the_object_before_queuing_the_task(self):
        self.login(self.regular_user)
        self.assertFalse(ILockable(self.subdocument).locked())

        self.move_items([self.subdocument],
                        source=self.subdossier,
                        target=self.empty_dossier)

        self.assertEqual(1, len(self._pending_tasks()))
        self.assertTrue(ILockable(self.subdocument).locked())

    @browsing
    def test_move_item_move_instantly_never_applies_move_lock(self, browser):
        self.login(self.regular_user, browser)

        document = self.document
        browser.open(document, view='move_item')
        browser.fill({'Destination': self.empty_dossier})
        browser.css('#form-buttons-button_submit').first.click()

        self.assertEqual(0, len(self._pending_tasks()))
        self.assertFalse(ILockable(document).locked())


class TestMoveObjectsTask(IntegrationTestCase):
    """Tests for the `MoveObjectsTask` handler."""

    def setUp(self):
        super(TestMoveObjectsTask, self).setUp()
        self.login(self.administrator)

    def _make_task(self, destination_uid, clipboard, user_id, object_uids=None):
        task = BackgroundTask()
        task.admin_unit_id = u'plone'
        task.task_type = TASK_TYPE
        task.status = TASK_STATUS_PENDING
        task.priority = 5
        arguments = {
            u'destination_uid': destination_uid,
            u'clipboard': clipboard,
            u'user_id': user_id}
        if object_uids is not None:
            arguments[u'object_uids'] = object_uids
        task.task_arguments = json.dumps(arguments)
        task.created = datetime.now()
        task.retries = 0
        task.max_retries = 3
        create_session().add(task)
        transaction.commit()
        return task

    def _no_op_commit_checkpoint(self, data):
        pass

    def test_execute_moves_the_object(self):
        moving_obj = self.subdocument
        clipboard = self.subdossier.manage_cutObjects(moving_obj.getId())
        task = self._make_task(
            self.empty_dossier.UID(), clipboard, self.administrator.getId())

        with self.observe_children(self.empty_dossier) as children:
            handler = MoveObjectsTask()
            handler.execute(task, self._no_op_commit_checkpoint)

        self.assertEqual(1, len(children['added']))
        self.assertEqual(moving_obj.UID(), children['added'].pop().UID())

    def test_execute_runs_paste_as_the_queuing_user(self):
        # The test is logged in as the administrator, but the task was
        # queued by regular_user - the paste must run as regular_user, not
        # as whoever happens to be logged in when the worker executes it,
        # and definitely not as the worker's own unrestricted `system` user.
        clipboard = self.subdossier.manage_cutObjects(self.subdocument.getId())
        task = self._make_task(
            self.empty_dossier.UID(), clipboard, self.regular_user.getId())

        import opengever.bgtasks.move as move_mod
        real_paste = move_mod.paste_clipboard
        captured_user_ids = []

        def spy_paste(destination, cb):
            captured_user_ids.append(getSecurityManager().getUser().getId())

        move_mod.paste_clipboard = spy_paste
        try:
            handler = MoveObjectsTask()
            handler.execute(task, self._no_op_commit_checkpoint)
        finally:
            move_mod.paste_clipboard = real_paste

        self.assertEqual([self.regular_user.getId()], captured_user_ids)
        # The original (administrator) security manager must be restored.
        self.assertEqual(
            self.administrator.getId(), getSecurityManager().getUser().getId())

    def test_execute_skips_missing_destination_without_raising(self):
        task = self._make_task(
            u'nonexistent-uid-0000-0000-000000000000',
            u'irrelevant-clipboard',
            self.administrator.getId())

        handler = MoveObjectsTask()
        # Should not raise.
        handler.execute(task, self._no_op_commit_checkpoint)

    def test_execute_skips_missing_arguments_without_raising(self):
        task = self._make_task(
            destination_uid=None, clipboard=None, user_id=None)

        handler = MoveObjectsTask()
        # Should not raise.
        handler.execute(task, self._no_op_commit_checkpoint)

    def test_execute_never_pastes_when_user_cannot_be_resolved(self):
        clipboard = self.subdossier.manage_cutObjects(self.subdocument.getId())
        task = self._make_task(
            self.empty_dossier.UID(), clipboard, u'nonexistent-user-0000')

        import opengever.bgtasks.move as move_mod
        real_paste = move_mod.paste_clipboard
        calls = []
        move_mod.paste_clipboard = lambda destination, cb: calls.append(destination)
        try:
            handler = MoveObjectsTask()
            handler.execute(task, self._no_op_commit_checkpoint)
        finally:
            move_mod.paste_clipboard = real_paste

        self.assertEqual(0, len(calls))

    def test_execute_swallows_expected_paste_failures(self):
        task = self._make_task(
            self.empty_dossier.UID(),
            u'irrelevant-clipboard',
            self.administrator.getId())

        import opengever.bgtasks.move as move_mod
        real_paste = move_mod.paste_clipboard

        for exc_cls in (ValueError, CopyError, ResourceLockedError, Unauthorized):
            def raising_paste(destination, clipboard, exc_cls=exc_cls):
                raise exc_cls('boom')
            move_mod.paste_clipboard = raising_paste
            try:
                handler = MoveObjectsTask()
                # Should not raise.
                handler.execute(task, self._no_op_commit_checkpoint)
            finally:
                move_mod.paste_clipboard = real_paste

    def test_execute_unlocks_object_after_successful_move(self):
        moving_obj = self.subdocument
        ILockable(moving_obj).lock(MOVE_LOCK)
        clipboard = self.subdossier.manage_cutObjects(moving_obj.getId())
        task = self._make_task(
            self.empty_dossier.UID(), clipboard, self.administrator.getId(),
            object_uids=[moving_obj.UID()])

        handler = MoveObjectsTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertFalse(ILockable(moving_obj).locked())

    def test_execute_unlocks_object_after_expected_paste_failure(self):
        moving_obj = self.subdocument
        ILockable(moving_obj).lock(MOVE_LOCK)
        task = self._make_task(
            self.empty_dossier.UID(),
            u'irrelevant-clipboard',
            self.administrator.getId(),
            object_uids=[moving_obj.UID()])

        import opengever.bgtasks.move as move_mod
        real_paste = move_mod.paste_clipboard

        def raising_paste(destination, clipboard):
            raise ValueError('boom')
        move_mod.paste_clipboard = raising_paste
        try:
            handler = MoveObjectsTask()
            handler.execute(task, self._no_op_commit_checkpoint)
        finally:
            move_mod.paste_clipboard = real_paste

        self.assertFalse(ILockable(moving_obj).locked())

    def test_execute_unlocks_object_when_destination_cannot_be_resolved(self):
        moving_obj = self.subdocument
        ILockable(moving_obj).lock(MOVE_LOCK)
        task = self._make_task(
            u'nonexistent-uid-0000-0000-000000000000',
            u'irrelevant-clipboard',
            self.administrator.getId(),
            object_uids=[moving_obj.UID()])

        handler = MoveObjectsTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertFalse(ILockable(moving_obj).locked())

    def test_execute_unlocks_object_when_arguments_are_missing(self):
        moving_obj = self.subdocument
        ILockable(moving_obj).lock(MOVE_LOCK)
        task = self._make_task(
            destination_uid=None, clipboard=None, user_id=None,
            object_uids=[moving_obj.UID()])

        handler = MoveObjectsTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertFalse(ILockable(moving_obj).locked())

    def test_execute_unlocks_object_when_user_cannot_be_resolved(self):
        moving_obj = self.subdocument
        ILockable(moving_obj).lock(MOVE_LOCK)
        clipboard = self.subdossier.manage_cutObjects(moving_obj.getId())
        task = self._make_task(
            self.empty_dossier.UID(), clipboard, u'nonexistent-user-0000',
            object_uids=[moving_obj.UID()])

        handler = MoveObjectsTask()
        handler.execute(task, self._no_op_commit_checkpoint)

        self.assertFalse(ILockable(moving_obj).locked())
