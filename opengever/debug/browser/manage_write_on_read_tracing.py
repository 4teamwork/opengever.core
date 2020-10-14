from collections import namedtuple
from datetime import datetime
from datetime import timedelta
from opengever.base.protect import OGProtectTransform
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.Connection import Connection
from ZODB.POSException import ConflictError
from ZODB.utils import u64
import inspect
import logging
import threading
import traceback


log = logging.getLogger('opengever.debug')


# References to original methods - used to restore them when "unpatching"
_orig_register_func = Connection.register
_orig_build_csrf_report_func = OGProtectTransform._build_csrf_report

# Module global to store traceback (and OID) on DB write. This will be
# used when building the CSRF report
_tb_for_last_db_write = None

# Monkey-patches expire after a timeout (in minutes) and remove themselves
DEFAULT_PATCH_TIMEOUT = 60
_patches_expire_at = None

# Locks to make writing to module globals thread-safe
expires_lock = threading.RLock()
tb_lock = threading.RLock()


# Lightweight object to keep a formatted traceback and associated info around
AnnotatedTraceback = namedtuple(
    'AnnotatedTraceback', ['oid', 'filename', 'line_no', 'extracted_tb'])


def _build_csrf_report_with_tb(self, env):
    """Patched version of _build_csrf_report that also logs the traceback
    """
    revert_patches_if_expired()

    for line in _orig_build_csrf_report_func(self, env):
        yield line

    instruction = _tb_for_last_db_write
    if instruction is not None:
        yield format_instruction(instruction)


def register_patched_to_trace(self, obj):
    """Patched version of ZODB.Connection.Connection.register to trace
    DB writes and collect stack traces.

    CAUTION: This will be called for every change to a persistent object,
    be very careful here!
    """
    revert_patches_if_expired()

    _orig_register_func(self, obj)
    try:
        save_stacktrace(obj)
    except ConflictError:
        raise
    except Exception, e:
        log.warn('Error when trying to save stacktrace: {}'.format(str(e)))


def revert_patches_if_expired():
    if datetime.now() >= _patches_expire_at:
        log.info("WriteOnRead tracing patches have expired. Reverting...")
        _unpatch_register()
        _unpatch_build_csrf_report()


def save_stacktrace(obj):
    """Stores an `AnnotatedTraceback` object that contains a formatted stack
    trace for the current frame and the OID of the object that has been
    modified for possible logging at a later point in time.
    """
    global _tb_for_last_db_write

    tb_limit = 20
    current_frame = inspect.currentframe()

    # Outer two frames are in this module, so they're not interesting
    frame = current_frame.f_back.f_back

    filename = frame.f_code.co_filename
    line_no = frame.f_lineno
    extracted_tb = traceback.extract_stack(frame, limit=tb_limit)
    oid = hex(u64(obj._p_oid))
    instruction = AnnotatedTraceback(oid, filename, line_no, extracted_tb)

    # Write the traceback to the module global (in a thread-safe way)
    with tb_lock:
        _tb_for_last_db_write = instruction

    # Avoid leaking frames
    del current_frame
    del frame


def format_instruction(instruction):
    """Render the information from an `AnnotatedTraceback` object (file name,
    line number and formatted traceback) and an OID for display.
    """
    output = ['\n']
    msg = 'DB write to obj with OID {oid} from code ' \
          'in "{filename}", line {line_no}!'
    msg = msg.format(**instruction._asdict())
    output.append("=" * len(msg))
    output.append(msg)
    output.append("=" * len(msg))
    output.append(''.join(traceback.format_list(instruction.extracted_tb)))
    return '\n'.join(output)


def _patch_register():
    assert _orig_register_func != register_patched_to_trace
    Connection.register = register_patched_to_trace
    log.info("Patched ZODB.Connection.Connection.register")


def _patch_build_csrf_report():
    from opengever.base.protect import OGProtectTransform
    assert _orig_build_csrf_report_func != _build_csrf_report_with_tb
    OGProtectTransform._build_csrf_report = _build_csrf_report_with_tb
    log.info("Patched OGProtectTransform._build_csrf_report")


def _unpatch_register():
    assert _orig_register_func != register_patched_to_trace
    Connection.register = _orig_register_func
    log.info("Reverted patch for ZODB.Connection.Connection.register")


def _unpatch_build_csrf_report():
    from opengever.base.protect import OGProtectTransform
    assert _orig_build_csrf_report_func != _build_csrf_report_with_tb
    OGProtectTransform._build_csrf_report = _orig_build_csrf_report_func
    log.info("Reverted patch for OGProtectTransform._build_csrf_report")


def _is_patched(func, orig_func):
    if func != orig_func:
        patched_func_name = func.func_name
        return (True, patched_func_name)
    return (False, '')


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
        timeout = int(self.request.form.get('timeout', DEFAULT_PATCH_TIMEOUT))

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
        global _patches_expire_at

        log.info("Activating WriteOnRead tracing...")
        with expires_lock:
            _patches_expire_at = datetime.now() + timedelta(minutes=timeout)

        _patch_register()
        _patch_build_csrf_report()
        msg = u'WriteOnRead tracing has been activated!'
        IStatusMessage(self.request).addStatusMessage(msg, 'warning')
        log.info(msg)

    def _deactivate_write_on_read_tracing(self):
        log.info("Deactivating WriteOnRead tracing...")
        _unpatch_register()
        _unpatch_build_csrf_report()
        msg = u'WriteOnRead tracing has been deactivated!'
        IStatusMessage(self.request).addStatusMessage(msg, 'info')
        log.info(msg)

    def default_timeout(self):
        if self._suggested_timeout is not None:
            return self._suggested_timeout
        return DEFAULT_PATCH_TIMEOUT

    def patching_status(self):
        for name, func, orig_func in (
            ('ZODB.Connection.Connection.register',
             Connection.register,
             _orig_register_func),
            ('opengever.base.protect.OGProtectTransform._build_csrf_report',
             OGProtectTransform._build_csrf_report,
             _orig_build_csrf_report_func)):
            patched, patched_name = _is_patched(func, orig_func)
            yield dict(name=name, patched_name=patched_name, patched=patched)

    def is_patched(self):
        return any(status['patched'] for status in self.patching_status())

    def current_expires(self):
        return _patches_expire_at

    def documentation(self):
        doc = ManageWriteOnReadTracing.__doc__
        return doc.replace('\n\n', '<br/><br/>')
