from logging.handlers import TimedRotatingFileHandler
from opengever.base.pathfinder import PathFinder
from opengever.core.debughelpers import all_plone_sites
from opengever.core.debughelpers import setup_plone
from opengever.nightlyjobs.runner import nightly_jobs_feature_enabled
from opengever.nightlyjobs.runner import NightlyJobRunner
from plone import api
from zope.globalrequest import getRequest
import argparse
import logging
import os
import sys
import traceback


try:
    from ftw.raven.reporter import maybe_report_exception
except ImportError:
    # Local development, ftw.raven may not be present
    def maybe_report_exception(context, request, exc_type, exc, traceback):
        pass


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

logger = None


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Run nightly jobs')
    parser.add_argument(
        '-f', '--force', action='store_true',
        help="Force execution even if outside time window or when load is high")

    args = parser.parse_args(argv)
    return args


def setup_logger():
    logger = logging.getLogger('opengever.nightlyjobs')
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure nightly job output gets logged on console
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    # Add handler that writes to self-rotating file
    log_dir = PathFinder().var_log
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'nightly-jobs.log'),
        when='midnight', backupCount=7)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    return logger


def run_nightly_jobs_handler(app, args):
    global logger

    # Make sure unhandled exceptions get logged to Sentry
    register_sentry_except_hook()

    logger = setup_logger()

    # Discard the first three arguments, because they're not "actual" arguments
    # but cruft that we get because of the way bin/instance [zopectl_cmd]
    # scripts work.
    args = parse_args(sys.argv[3:])
    force = args.force

    for plone_site in all_plone_sites(app):
        plone_site = setup_plone(plone_site)
        invoke_nightly_job_runner(plone_site, force, logger)


def setup_language(plone):
    lang_tool = api.portal.get_tool('portal_languages')
    lang = lang_tool.getPreferredLanguage()
    plone.REQUEST.environ['HTTP_ACCEPT_LANGUAGE'] = lang
    plone.REQUEST.setupLocale()


def sentry_except_hook(exc_type, exc, tb):
    """Custom excepthook to log unhandled exceptions to Sentry and logfile.

    We need to install this one ourselves, because ZPublisher isn't in
    play during a bin/instance [zopectl_cmd] script, so we don't get to
    piggy-back on zpublisher_exception_hook_wrapper.

    This isn't perfect: We don't have a context (because no traversal is
    happening) and we get a URL like 'http://foo' reported to Sentry, but
    it should be good enough to at least notice things going wrong.
    """
    # Log exception to logfile
    logger.error(''.join(traceback.format_exception(exc_type, exc, tb)))

    # Log exception to sentry
    context = None
    request = getRequest()
    maybe_report_exception(context, request, exc_type, exc, tb)
    return sys.__excepthook__(exc_type, exc, tb)


def register_sentry_except_hook():
    sys.excepthook = sentry_except_hook


def invoke_nightly_job_runner(plone_site, force, logger):
    logger.info('Running nightly jobs...')
    logger.info('=' * 80)

    if not nightly_jobs_feature_enabled() and not force:
        logger.info('Nightly jobs feature is not enabled in registry - '
                    'not running any jobs for %r' % plone_site)
        return

    setup_language(plone_site)

    runner = NightlyJobRunner(
        setup_own_task_queue=True,
        force_execution=force,
        logger=logger)

    logger.info('Found {} providers: {}'.format(len(runner.job_providers),
                                                runner.job_providers.keys()))
    logger.info('Number of jobs: {}'.format(runner.get_initial_jobs_count()))

    exc = runner.execute_pending_jobs()
    if exc:
        logger.info('Early abort')
        logger.info(runner.format_early_abort_message(exc))

    logger.info('Successfully executed {} jobs'.format(runner.get_executed_jobs_count()))

    if runner.get_remaining_jobs_count() == 0:
        logger.info('No jobs remaining')
    else:
        logger.info('{} jobs remaining'.format(runner.get_remaining_jobs_count()))
    logger.info('Finished running nightly jobs.')
