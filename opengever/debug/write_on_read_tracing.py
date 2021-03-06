"""Tooling to aid in debugging writes on read.

Used via the @@manage-write-on-read-tracing view.
"""
from datetime import datetime
from opengever.base.protect import OGProtectTransform
from opengever.debug.stacktrace import format_instruction
from opengever.debug.stacktrace import save_stacktrace
from ZODB.Connection import Connection
from ZODB.POSException import ConflictError
import logging
import threading


log = logging.getLogger('opengever.debug')


# Module global to store traceback (and OID) on DB write. This will be
# used when building the CSRF report
tb_for_last_db_write = None

# References to original methods - used to restore them when "unpatching"
orig_register_func = None
orig_build_csrf_report_func = None

# Monkey-patches expire after a timeout (in minutes) and remove themselves
DEFAULT_PATCH_TIMEOUT = 60
patches_expire_at = None

# Locks to make writing to module globals thread-safe
expires_lock = threading.RLock()
tb_lock = threading.RLock()
patch_lock = threading.RLock()


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
    orig_register_func(self, obj)

    revert_patches_if_expired()
    try:
        global tb_for_last_db_write
        instruction = save_stacktrace(obj)
        # Write the traceback to the module global (in a thread-safe way)
        with tb_lock:
            tb_for_last_db_write = instruction
    except ConflictError:
        raise
    except Exception, e:
        log.warn('Error when trying to save stacktrace: {}'.format(str(e)))


def revert_patches_if_expired():
    if datetime.now() >= patches_expire_at:
        log.info("WriteOnRead tracing patches have expired. Reverting...")
        unpatch()


def patch():
    with patch_lock:
        global orig_register_func
        assert orig_register_func is None
        orig_register_func = Connection.register
        assert orig_register_func.__func__ != register_patched_to_trace
        Connection.register = register_patched_to_trace
        log.info("Patched ZODB.Connection.Connection.register")

        global orig_build_csrf_report_func
        assert orig_build_csrf_report_func is None
        orig_build_csrf_report_func = OGProtectTransform._build_csrf_report
        assert orig_build_csrf_report_func.__func__ != build_csrf_report_with_tb
        OGProtectTransform._build_csrf_report = build_csrf_report_with_tb
        log.info("Patched OGProtectTransform._build_csrf_report")


def unpatch():
    with patch_lock:
        global orig_register_func
        assert orig_register_func is not None
        assert orig_register_func.__func__ != register_patched_to_trace
        Connection.register = orig_register_func
        orig_register_func = None
        log.info("Reverted patch for ZODB.Connection.Connection.register")

        global orig_build_csrf_report_func
        assert orig_build_csrf_report_func is not None
        assert orig_build_csrf_report_func.__func__ != build_csrf_report_with_tb
        OGProtectTransform._build_csrf_report = orig_build_csrf_report_func
        orig_build_csrf_report_func = None
        log.info("Reverted patch for OGProtectTransform._build_csrf_report")


def is_func_patched(func, patch_func):
    if func == patch_func:
        patched_func_name = func.func_name
        return (True, patched_func_name)
    return (False, '')
