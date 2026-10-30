from datetime import datetime
from ftw.solr.interfaces import ISolrSearch
from opengever.base.model import create_session
from opengever.base.sentry import log_msg_to_sentry
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_FAILED
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.model import TASK_STATUS_RUNNING
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.bgtasks.task import get_task_class
from zope.component import queryUtility
from zope.globalrequest import getRequest
import json
import logging
import signal
import sys
import threading
import traceback
import transaction


logger = logging.getLogger('opengever.bgtasks')

IDLE_SLEEP_SECONDS = 5


class BackgroundTaskWorker(object):

    def __init__(self, log=None):
        self.log = log or logger
        self._stop_event = threading.Event()

    def request_stop(self):
        self._stop_event.set()

    def _install_signal_handlers(self):
        """Request a graceful stop on SIGINT/SIGTERM.

        A second signal restores the original handler, so that the process
        can still be terminated forcefully.
        """
        original_handlers = {}

        def handle_signal(signum, frame):
            self.request_stop()
            self._restore_signal_handlers(original_handlers)

        for sig in (signal.SIGINT, signal.SIGTERM):
            original_handlers[sig] = signal.signal(sig, handle_signal)
        return original_handlers

    def _restore_signal_handlers(self, handlers):
        for sig, handler in handlers.items():
            # signal.signal returns None for handlers not installed from Python
            signal.signal(sig, handler if handler is not None else signal.SIG_DFL)

    def run_forever(self, admin_unit_id):
        self._stop_event.clear()
        original_handlers = {}
        # Signal handlers can only be installed from the main thread
        if isinstance(threading.current_thread(), threading._MainThread):
            original_handlers = self._install_signal_handlers()

        try:
            self.reset_interrupted_tasks(admin_unit_id)

            self.log.info('Background task worker ready for admin unit: %s' % admin_unit_id)
            while not self._stop_event.is_set():
                task = self.claim_next_task(admin_unit_id)
                if task:
                    self.execute_task(task)
                else:
                    self.log.debug('No pending tasks, sleeping %ds' % IDLE_SLEEP_SECONDS)
                    self._stop_event.wait(IDLE_SLEEP_SECONDS)
        finally:
            self._restore_signal_handlers(original_handlers)

        self.log.info('Background task worker stopped (shutdown requested)')

    def reset_interrupted_tasks(self, admin_unit_id):
        session = create_session()
        running = (session.query(BackgroundTask)
                   .filter_by(admin_unit_id=admin_unit_id,
                              status=TASK_STATUS_RUNNING)
                   .all())
        for task in running:
            self.log.warning(
                'Resetting interrupted task %s (%s) to pending' % (
                    task.task_id, task.task_type))
            task.status = TASK_STATUS_PENDING
            task.started = None

        if running:
            transaction.commit()

    def claim_next_task(self, admin_unit_id):
        session = create_session()
        now = datetime.now()
        task = (session.query(BackgroundTask)
                .filter(BackgroundTask.admin_unit_id == admin_unit_id,
                        BackgroundTask.status == TASK_STATUS_PENDING,
                        (BackgroundTask.scheduled_for.is_(None))
                        | (BackgroundTask.scheduled_for <= now))
                .order_by(BackgroundTask.priority.asc(),
                          BackgroundTask.created.asc())
                .first())
        return task

    def execute_task(self, task):
        self.log.info('Executing task %s (type=%s, priority=%d, retries=%d/%d)' % (
            task.task_id, task.task_type, task.priority,
            task.retries, task.max_retries))

        task.status = TASK_STATUS_RUNNING
        task.started = datetime.now()
        transaction.commit()
        solr = queryUtility(ISolrSearch)

        def commit_checkpoint(data, processed, total=None):
            # Reenroll the session in the current transaction
            session = create_session()
            task = session.query(BackgroundTask).get(task_id)
            task.checkpoint_data = json.dumps(data)
            transaction.commit()
            # Always commit Solr updates, even when no ZODB objects were modified.
            if solr is not None:
                solr.manager.connection.commit(after_commit=False)
            if total is None:
                self.log.info(
                    'Checkpoint committed for task %s. Processed %d items.',
                    task.task_id,
                    processed,
                )
            else:
                self.log.info(
                    'Checkpoint committed for task %s. Processed %d of %d items (%.2f %%).',
                    task.task_id,
                    processed,
                    total,
                    100 * float(processed) / total,
                )

        task_id = task.task_id
        task_type = task.task_type

        try:
            task_cls = get_task_class(task.task_type)
            handler = task_cls()
            handler.execute(task, commit_checkpoint)
        except Exception:
            transaction.abort()
            e_type, e_value, tb = sys.exc_info()
            formatted = ''.join(traceback.format_exception(e_type, e_value, tb))
            del e_type, e_value, tb
            self.log.error(
                'Task %s (%s) failed:\n%s' % (task_id, task_type, formatted))
            session = create_session()
            task = session.query(BackgroundTask).get(task_id)
            if task is not None:
                self._handle_failure(task, formatted)
            return

        # Reenroll the session in the current transaction
        session = create_session()
        task = session.query(BackgroundTask).get(task_id)
        task.status = TASK_STATUS_SUCCEEDED
        task.finished = datetime.now()
        transaction.commit()
        # Always commit Solr updates, even when no ZODB objects were modified.
        if solr is not None:
            solr.manager.connection.commit(after_commit=False)
            self.log.info('Task %s succeeded' % task_id)

    def _handle_failure(self, task, error_message):
        task.error_message = error_message
        task.retries += 1

        if task.retries <= task.max_retries:
            task.status = TASK_STATUS_PENDING
            task.started = None
            self.log.info(
                'Task %s re-queued (attempt %d of %d)' % (
                    task.task_id, task.retries, task.max_retries))
        else:
            task.status = TASK_STATUS_FAILED
            task.finished = datetime.now()
            message = 'Background task %s (%s) permanently failed after %d attempts' % (
                task.task_id, task.task_type, task.retries)
            self.log.error(message)
            log_msg_to_sentry(message, request=getRequest())

        transaction.commit()
