from opengever.propertysheets import _


def render_error(errors):
    first_error = errors[0]
    error_string = repr(first_error[1]).decode('utf-8')
    msg = _(
        u'msg_propertysheet_has_errors',
        default=u"The propertysheet form contains an error:\n ${error_string}",
        mapping={'error_string': error_string})
    return msg
