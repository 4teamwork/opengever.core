from datetime import datetime
from datetime import timedelta
from opengever.base.protect import OGProtectTransform
from opengever.debug import write_on_read_tracing
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.Connection import Connection
import logging


log = logging.getLogger('opengever.debug')


class ManageWriteOnReadTracing(BrowserView):
    """This view allows to enable WriteOnRead tracing, which will monkey patch
    the method for object registration on the ZODB connection in order to
    save a stack trace at the point a persistent object has been registered
    (i.e. changed for the first time in a transaction).

    Activating WriteOnRead tracing will patch two methods: register() on the ZODB
    connection and _build_csrf_report() on our own OGProtectTransform. The
    patch to register() will save a formatted stack trace to a module global
    every time a persistent object is modified for the first time in a
    transaction. This will then allow the patched _build_csrf_report() to
    include that stored stack trace in the CSRF incident log if a CSRF
    confirmation dialog is triggered.

    Those patches can also be reverted from this view: The respective methods
    will then be restored to their original state.

    Additionally, there is a timeout after which the patches will expire, and
    remove themselves the next time they're called.
    """

    def __call__(self):
        action = self.request.form.get('submit')
        timeout = int(self.request.form.get(
            'timeout', write_on_read_tracing.DEFAULT_PATCH_TIMEOUT))

        if action == 'Activate':
            self._activate_write_on_read_tracing(timeout)

        elif action == 'Deactivate':
            self._deactivate_write_on_read_tracing()

        # Allow for suggesting a timeout value via query string
        self._suggested_timeout = None
        suggested_timeout = self.request.form.get('suggested_timeout')
        if suggested_timeout is not None:
            self._suggested_timeout = int(suggested_timeout)

        return super(ManageWriteOnReadTracing, self).__call__()

    def _activate_write_on_read_tracing(self, timeout):
        log.info("Activating WriteOnRead tracing...")
        with write_on_read_tracing.expires_lock:
            write_on_read_tracing.patches_expire_at = datetime.now() + timedelta(minutes=timeout)

        write_on_read_tracing.patch()
        msg = u'WriteOnRead tracing has been activated!'
        IStatusMessage(self.request).addStatusMessage(msg, 'warning')
        log.info(msg)

    def _deactivate_write_on_read_tracing(self):
        log.info("Deactivating WriteOnRead tracing...")
        write_on_read_tracing.unpatch()
        msg = u'WriteOnRead tracing has been deactivated!'
        IStatusMessage(self.request).addStatusMessage(msg, 'info')
        log.info(msg)

    def default_timeout(self):
        if self._suggested_timeout is not None:
            return self._suggested_timeout
        return write_on_read_tracing.DEFAULT_PATCH_TIMEOUT

    def patching_status(self):
        for name, func, patch_func in (
            ('ZODB.Connection.Connection.register',
             Connection.register.__func__,  # make sure to compare functions
             write_on_read_tracing.register_patched_to_trace),
            ('opengever.base.protect.OGProtectTransform._build_csrf_report',
             OGProtectTransform._build_csrf_report.__func__,   # make sure to compare functions
             write_on_read_tracing.build_csrf_report_with_tb)):
            patched, patched_name = write_on_read_tracing.is_func_patched(func, patch_func)
            yield dict(name=name, patched_name=patched_name, patched=patched)

    def is_patched(self):
        return any(status['patched'] for status in self.patching_status())

    def current_expires(self):
        return write_on_read_tracing.patches_expire_at

    def documentation(self):
        doc = ManageWriteOnReadTracing.__doc__
        return doc.replace('\n\n', '<br/><br/>')
