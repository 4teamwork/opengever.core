from contextlib import contextmanager
from zope.globalrequest import getRequest
import logging
import pkg_resources


# Conditional imports to ease local development (without ftw.raven)
try:
    pkg_resources.get_distribution('ftw.raven')

except pkg_resources.DistributionNotFound:
    FTW_RAVEN_AVAILABLE = False

    def maybe_report_exception(*args, **kwargs):
        """Noop function that gets used during local development.
        """
        pass
else:
    FTW_RAVEN_AVAILABLE = True
    from ftw.raven.client import get_raven_client
    from ftw.raven.reporter import get_default_tags
    from ftw.raven.reporter import get_release
    from ftw.raven.reporter import maybe_report_exception  # noqa
    from ftw.raven.reporter import prepare_extra_infos
    from ftw.raven.reporter import prepare_modules_infos
    from ftw.raven.reporter import prepare_request_infos
    from ftw.raven.reporter import prepare_user_infos


log = logging.getLogger('opengever.base.sentry')


class SentryHandler(logging.Handler):
    """Minimalistic log handler to also log records to sentry.

    For simplicity contains a hard-coded mapping of log-levels we are
    currently interested in.

    Not intented to stay around for long but rather a quick way to get logging
    to sentry for potentially critical solr errors *now*. Should go away again
    once we have proper logging for non-exceptions to sentry.
    """

    logging_level_to_sentry_level = {
        logging.ERROR: 'error',
        logging.WARNING: 'warning',
        logging.CRITICAL: 'critical',
        logging.FATAL: 'fatal',
    }

    def emit(self, record):
        level = self.logging_level_to_sentry_level.get(record.levelno)
        if not level:
            return

        message = record.getMessage()
        log_msg_to_sentry(message, level=level)


# explicitly register sentry logging for some special loggers we are currently
# interested in
logging.getLogger('ftw.solr.connection').addHandler(SentryHandler())
logging.getLogger('ftw.solr.handlers').addHandler(SentryHandler())


def context_from_request(request):
    """Find the context from the request.

    Based on:
    http://docs.plone.org/develop/plone/serving/http_request_and_response.html#published-object
    """
    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is None:
        try:
            context = request.get('PARENTS', [])[0]
        except:  # noqa
            pass
    return context


def url_from_request(request):
    return request.get('ACTUAL_URL', '')


_marker = object()


def log_msg_to_sentry(message, context=None, request=None, url=None,
                      data=None, extra=None, fingerprint=None,
                      level='error', string_max_length=_marker):
    """A (hopefully) fail-safe function to log a message to Sentry.

    This is loosely based on ftw.raven's maybe_report_exception(), except that
    it can be used to simply log a free-form message and optionally some
    additional data, for cases where you don't have an actual exception.

    It also allows to specifiy a fingerprint to better control Sentry's
    grouping of messages.

    This still depends on ftw.raven for extraction of some additional info.
    If either ftw.raven isn't installed, or we can't get hold of a Sentry
    client, this function should abort gracefully, not log to Sentry, but also
    not cause any additional problems.

    This is why everything here is written in a very defensive way, we're
    being very paranoid and try hard not to cause any additional issues.
    """
    if not FTW_RAVEN_AVAILABLE:
        log.warn('ftw.raven not installed, not logging to Sentry')
        return False

    try:
        client = get_raven_client()
        if client is None:
            log.warn('Could not get raven client, not logging to Sentry')
            return False

        if request is None:
            request = getRequest()

        if context is None:
            context = context_from_request(request)

        if url is None:
            url = url_from_request(request)

        try:
            data_dict = {
                'request': prepare_request_infos(request),
                'user': prepare_user_infos(context, request),
                'extra': prepare_extra_infos(context, request),
                'modules': prepare_modules_infos(),
                'tags': get_default_tags(),
                'level': level,
            }

            release = get_release()
            if release:
                data_dict['release'] = release

            if data is not None:
                data_dict.update(data)

        except:  # noqa
            log.error('Error while preparing sentry data.')
            raise

        try:
            kwargs = dict(
                message=message,
                data=data_dict,
                extra=extra,
                stack=False,
            )

            if fingerprint:
                kwargs['fingerprint'] = fingerprint

            with custom_string_max_length(client, string_max_length):
                client.captureMessage(**kwargs)

        except:  # noqa
            log.error('Error while reporting to sentry.')
            raise

    except:  # noqa
        try:
            get_raven_client().captureException(
                data={'extra': {
                    'raven_meta_error': 'Error occured while reporting'
                    ' another error.'}})
        except:  # noqa
            log.error(
                'Failed to report error occured while reporting error.')
            return False
    return True


@contextmanager
def custom_string_max_length(client, string_max_length):
    try:
        prev_string_max_length = client.string_max_length
        if string_max_length != _marker:
            client.string_max_length = string_max_length
        yield
    finally:
        client.string_max_length = prev_string_max_length
