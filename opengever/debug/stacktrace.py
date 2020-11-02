from collections import namedtuple
from ZODB.utils import u64
import inspect
import traceback


# Lightweight object to keep a formatted traceback and associated info around
AnnotatedTraceback = namedtuple(
    'AnnotatedTraceback', ['oid', 'filename', 'line_no', 'extracted_tb'])


def save_stacktrace(obj):
    """Returns an `AnnotatedTraceback` object that contains a formatted stack
    trace for the current frame and the OID of the object that has been
    modified for possible logging at a later point in time.
    """
    tb_limit = 20
    current_frame = inspect.currentframe()

    # Outer two frames are in this module, so they're not interesting
    frame = current_frame.f_back.f_back

    filename = frame.f_code.co_filename
    line_no = frame.f_lineno
    extracted_tb = traceback.extract_stack(frame, limit=tb_limit)
    oid = hex(u64(obj._p_oid))
    instruction = AnnotatedTraceback(oid, filename, line_no, extracted_tb)

    # Avoid leaking frames
    del current_frame
    del frame

    return instruction


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
