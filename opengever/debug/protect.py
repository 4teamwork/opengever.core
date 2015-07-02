"""Helpers to assist in debugging issues around plone.protect
"""

from collections import namedtuple
from functools import partial
import sys
import traceback
import ZODB


original_trace_func = None


Instruction = namedtuple(
    'Instruction', ['filename', 'line_no', 'extracted_tb'])


class TraceObjectRegistrations(object):
    """
    Context manager that traces and displays calls to a ZODB
    connection's `register()` method.

    These calls will effectively indicate a DB write, and displaying them
    for an operation that isn't supposed to cause a DB write can help in
    debugging problems with plone.protect's automatic CSRF protection.

    Once a call to `register()` is intercepted, a message indicating this
    and the corresponding stack trace are displayed.

    :param limit: Maximum depth of the displayed stack trace

    Usage:

    >>> with TraceObjectRegistrations(tb_limit=5):
    ...     something_that_writes_but_shouldnt()

    """

    def __init__(self, tb_limit=10):
        self.tb_limit = tb_limit

    def __enter__(self):
        trace_func = partial(_trace_obj_registration_calls, self.tb_limit)
        set_trace(trace_func)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        remove_trace()


def set_trace(trace_func):
    """Registers a call trace function which will be called for every
    function call, and keeps a reference to any previously set trace function
    in order to be able to restore it.
    """
    global original_trace

    original_trace = sys.gettrace()
    sys.settrace(trace_func)


def remove_trace():
    """Restores the original trace function (if there was one).
    """
    global original_trace

    sys.settrace(original_trace_func)


def _trace_obj_registration_calls(tb_limit, frame, event, arg):
    """Call trace function to intercept any calls to a ZODB
    connection's .register() method (which effectively indicates a DB write).

    (This function needs to be partially applied first in order to have the
    proper 3 argument signature to be used as a trace function)
    """
    if event != 'call':
        return

    co = frame.f_code
    func_name = co.co_name

    # We only want to trace calls to .register() on a
    # ZODB.Connection.Connection or any of its subclasses.

    if func_name != 'register':
        return

    frame_self = frame.f_locals.get('self')
    if frame_self is None:
        return

    if not issubclass(frame_self.__class__, ZODB.Connection.Connection):
        return

    filename = frame.f_code.co_filename
    line_no = frame.f_lineno
    extracted_tb = traceback.extract_stack(frame, limit=tb_limit)
    instruction = Instruction(filename, line_no, extracted_tb)

    # At this point we can be reasonably certain that we're in
    # `register(self, obj)` - so we try to get a reference to the object
    # that's being registered to print a more helpful message
    obj = frame.f_locals.get('obj')

    _display_intercepted_call(obj, instruction)


def _display_intercepted_call(obj, instruction):
    msg = 'DB write to {obj} from code in "{filename}", line {line_no}!'
    msg = msg.format(obj=obj, **instruction._asdict())
    print "=" * len(msg)
    print msg
    print "=" * len(msg)
    print ''.join(traceback.format_list(instruction.extracted_tb))
