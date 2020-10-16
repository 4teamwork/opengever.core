"""Tooling to aid in debugging writes on read.

Used via the @@manage-write-on-read-tracing view.
"""
from collections import namedtuple
from datetime import datetime
from opengever.base.protect import OGProtectTransform
from ZODB.Connection import Connection
from ZODB.POSException import ConflictError
from ZODB.utils import u64
import inspect
import logging
import threading
import traceback


log = logging.getLogger('opengever.debug')


# Module global to store traceback (and OID) on DB write. This will be
# used when building the CSRF report
tb_for_last_db_write = None

# References to original methods - used to restore them when "unpatching"
orig_register_func = Connection.register
orig_build_csrf_report_func = OGProtectTransform._build_csrf_report

# Monkey-patches expire after a timeout (in minutes) and remove themselves
DEFAULT_PATCH_TIMEOUT = 60
patches_expire_at = None

# Locks to make writing to module globals thread-safe
expires_lock = threading.RLock()
tb_lock = threading.RLock()


# Lightweight object to keep a formatted traceback and associated info around
AnnotatedTraceback = namedtuple(
    'AnnotatedTraceback', ['oid', 'filename', 'line_no', 'extracted_tb'])


def build_csrf_report_with_tb(self, env):
    """Patched version of _build_csrf_report that also logs the traceback
    """
    revert_patches_if_expired()

    for line in orig_build_csrf_report_func(self, env):
        yield line

    instruction = tb_for_last_db_write
    if instruction is not None:
        yield format_instruction(instruction)


def register_patched_to_trace(self, obj):
    """Patched version of ZODB.Connection.Connection.register to trace
    DB writes and collect stack traces.

    CAUTION: This will be called for every change to a persistent object,
    be very careful here!
    """
    revert_patches_if_expired()

    orig_register_func(self, obj)
    try:
        save_stacktrace(obj)
    except ConflictError:
        raise
    except Exception, e:
        log.warn('Error when trying to save stacktrace: {}'.format(str(e)))


def revert_patches_if_expired():
    if datetime.now() >= patches_expire_at:
        log.info("WriteOnRead tracing patches have expired. Reverting...")
        unpatch_register()
        unpatch_build_csrf_report()


def save_stacktrace(obj):
    """Stores an `AnnotatedTraceback` object that contains a formatted stack
    trace for the current frame and the OID of the object that has been
    modified for possible logging at a later point in time.
    """
    global tb_for_last_db_write

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
        tb_for_last_db_write = instruction

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


def patch_register():
    assert orig_register_func != register_patched_to_trace
    Connection.register = register_patched_to_trace
    log.info("Patched ZODB.Connection.Connection.register")


def patch_build_csrf_report():
    from opengever.base.protect import OGProtectTransform
    assert orig_build_csrf_report_func != build_csrf_report_with_tb
    OGProtectTransform._build_csrf_report = build_csrf_report_with_tb
    log.info("Patched OGProtectTransform._build_csrf_report")


def unpatch_register():
    assert orig_register_func != register_patched_to_trace
    Connection.register = orig_register_func
    log.info("Reverted patch for ZODB.Connection.Connection.register")


def unpatch_build_csrf_report():
    from opengever.base.protect import OGProtectTransform
    assert orig_build_csrf_report_func != build_csrf_report_with_tb
    OGProtectTransform._build_csrf_report = orig_build_csrf_report_func
    log.info("Reverted patch for OGProtectTransform._build_csrf_report")


def is_func_patched(func, orig_func):
    if func != orig_func:
        patched_func_name = func.func_name
        return (True, patched_func_name)
    return (False, '')
