from ftw.raven.reporter import maybe_report_exception
from opengever.core.debughelpers import all_plone_sites
from opengever.core.debughelpers import setup_plone
from opengever.nightlyjobs.runner import nightly_jobs_feature_enabled
from opengever.nightlyjobs.runner import NightlyJobRunner
from plone import api
from zope.globalrequest import getRequest
import logging
import sys


logger = logging.getLogger('opengever.nightlyjobs')


def run_nightly_jobs_handler(app, args):
    # Make sure unhandled exceptions get logged to Sentry
    register_sentry_except_hook()

    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure send_digests()'s output gets logged on console
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    for plone_site in all_plone_sites(app):
        plone_site = setup_plone(plone_site)
        invoke_nightly_job_runner(plone_site)


def setup_language(plone):
    lang_tool = api.portal.get_tool('portal_languages')
    lang = lang_tool.getPreferredLanguage()
    plone.REQUEST.environ['HTTP_ACCEPT_LANGUAGE'] = lang
    plone.REQUEST.setupLocale()


def sentry_except_hook(exc_type, exc, traceback):
    """Custom excepthook to log unhandled exceptions to Sentry.

    We need to install this one ourselves, because ZPublisher isn't in
    play during a bin/instance [zopectl_cmd] script, so we don't get to
    piggy-back on zpublisher_exception_hook_wrapper.

    This isn't perfect: We don't have a context (because no traversal is
    happening) and we get a URL like 'http://foo' reported to Sentry, but
    it should be good enough to at least notice things going wrong.
    """
    context = None
    request = getRequest()
    maybe_report_exception(context, request, exc_type, exc, traceback)
    return sys.__excepthook__(exc_type, exc, traceback)


def register_sentry_except_hook():
    sys.excepthook = sentry_except_hook


def invoke_nightly_job_runner(plone_site):
    if not nightly_jobs_feature_enabled():
        logger.info('Nightly jobs feature is not enabled in registry - '
                    'not running any jobs for %r' % plone_site)
        return

    setup_language(plone_site)

    runner = NightlyJobRunner(setup_own_task_queue=True)
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
