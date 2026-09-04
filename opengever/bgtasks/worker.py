from datetime import datetime
from opengever.base.model import create_session
from opengever.base.sentry import log_msg_to_sentry
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_FAILED
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.model import TASK_STATUS_RUNNING
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.bgtasks.task import get_task_class
from zope.globalrequest import getRequest
import json
import logging
import sys
import time
import traceback
import transaction


logger = logging.getLogger('opengever.bgtasks')

IDLE_SLEEP_SECONDS = 5


class BackgroundTaskWorker(object):

    def __init__(self, log=None):
        self.log = log or logger

    def run_forever(self, admin_unit_id):
        self.log.info('Background task worker starting for admin unit: %s' % admin_unit_id)
        self.reset_interrupted_tasks(admin_unit_id)

        while True:
            task = self.claim_next_task(admin_unit_id)
            if task:
                self.execute_task(task)
            else:
                self.log.debug('No pending tasks, sleeping %ds' % IDLE_SLEEP_SECONDS)
                time.sleep(IDLE_SLEEP_SECONDS)

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

        def commit_checkpoint(data):
            task.checkpoint_data = json.dumps(data)
            transaction.commit()
            self.log.debug('Checkpoint committed for task %s' % task.task_id)

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
