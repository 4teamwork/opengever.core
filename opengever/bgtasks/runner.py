from logging.handlers import TimedRotatingFileHandler
from opengever.base.pathfinder import PathFinder
from opengever.base.sentry import maybe_report_exception
from opengever.bgtasks.worker import BackgroundTaskWorker
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.ogds.base.utils import get_current_admin_unit
from zope.globalrequest import getRequest
import logging
import os
import sys
import traceback


LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

_logger = None


def setup_logger():
    log = logging.getLogger('opengever.bgtasks')
    if log.root.handlers:
        stream_handler = log.root.handlers[0]
        stream_handler.setLevel(logging.INFO)
    log.setLevel(logging.INFO)

    log_dir = PathFinder().var_log
    file_handler = TimedRotatingFileHandler(
        os.path.realpath(os.path.join(log_dir, 'background-tasks.log')),
        when='midnight', backupCount=7)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    log.addHandler(file_handler)

    return log


def sentry_except_hook(exc_type, exc, tb):
    if _logger is not None:
        _logger.error(''.join(traceback.format_exception(exc_type, exc, tb)))
    context = None
    request = getRequest()
    maybe_report_exception(context, request, exc_type, exc, tb)
    return sys.__excepthook__(exc_type, exc, tb)


def register_sentry_except_hook():
    sys.excepthook = sentry_except_hook


def run_background_tasks_handler(app, args):
    global _logger

    _logger = setup_logger()
    register_sentry_except_hook()

    plone_site = setup_plone(get_first_plone_site(app))
    admin_unit = get_current_admin_unit()
    if admin_unit is None:
        _logger.error('No admin unit configured for site %r, cannot start worker' % plone_site.id)
        return

    _logger.info('Starting background task worker for admin unit: %s' % admin_unit.unit_id)
    worker = BackgroundTaskWorker(log=_logger)
    worker.run_forever(admin_unit.unit_id)
