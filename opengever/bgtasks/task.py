from datetime import datetime
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import DEFAULT_MAX_RETRIES
from opengever.bgtasks.model import DEFAULT_PRIORITY
from opengever.bgtasks.model import default_task_id
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from plone import api
import json
import logging


logger = logging.getLogger('opengever.bgtasks')

_task_registry = {}


def register_task_type(name, cls):
    _task_registry[name] = cls


def get_task_class(name):
    cls = _task_registry.get(name)
    if cls is None:
        raise KeyError(u'Unknown background task type: %s' % name)
    return cls


def is_background_tasks_enabled():
    """Whether queue_task() should enqueue tasks for the worker.

    Fails safe: if the registry record can't be read (no site, record
    missing, or any other error), background tasks are treated as disabled.
    """
    try:
        return api.portal.get_registry_record(
            'opengever.bgtasks.interfaces.IBackgroundTaskSettings.is_feature_enabled')
    except Exception:
        logger.warning('Could not read background tasks registry record, '
                       'defaulting to disabled', exc_info=True)
        return False


def queue_task(task_type, admin_unit_id, arguments=None, priority=DEFAULT_PRIORITY,
               run_at=None, max_retries=DEFAULT_MAX_RETRIES):
    if task_type not in _task_registry:
        raise ValueError(u'Unknown task type: %s' % task_type)

    task = BackgroundTask()
    task.task_id = default_task_id()
    task.admin_unit_id = admin_unit_id
    task.task_type = task_type
    task.status = TASK_STATUS_PENDING
    task.priority = priority
    task.scheduled_for = run_at
    task.created = datetime.now()
    task.retries = 0
    task.max_retries = max_retries

    if arguments is not None:
        task.task_arguments = json.dumps(arguments)

    if not is_background_tasks_enabled():
        handler = get_task_class(task_type)()
        handler.execute(task, lambda data: None)
        task.status = TASK_STATUS_SUCCEEDED
        return task

    session = create_session()
    session.add(task)
    return task


class BaseBackgroundTask(object):
    """Base class for all background task implementations.

    Subclasses must set `task_type` and implement `execute()`.
    Register with `register_task_type(task_type, MyTask)` at import time.
    """

    task_type = None

    def execute(self, task, commit_checkpoint):
        """Execute the task.

        `task` is the BackgroundTask ORM row.
        `commit_checkpoint(data)` persists a JSON-serializable dict and
        commits - call it periodically to enable resume after worker restart.
        The stored data is available as `task.checkpoint_data` (JSON string)
        on the next execution attempt.
        """
        raise NotImplementedError

    def get_arguments(self, task):
        if task.task_arguments:
            return json.loads(task.task_arguments)
        return {}

    def get_checkpoint(self, task):
        if task.checkpoint_data:
            return json.loads(task.checkpoint_data)
        return None
