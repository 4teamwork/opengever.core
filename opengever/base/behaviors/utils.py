from plone.namedfile.utils import get_contenttype
from urllib import quote
from z3c.form.interfaces import HIDDEN_MODE
import re


# Used as sortkey for sorting strings in numerical order
# TODO: Move to a more suitable place
def split_string_by_numbers(x):
    x = str(x)
    r = re.compile(r'(\d+)')
    left = r.split(x)
    return [int(y) if y.isdigit() else y for y in left]


def set_attachment_content_disposition(request, filename, file=None):
    """ Set the content disposition on the request for the given browser
    """
    if not filename:
        return

    if file:
        contenttype = get_contenttype(file)
        request.response.setHeader("Content-Type", contenttype)
        request.response.setHeader("Content-Length", file.getSize())

    user_agent = request.get('HTTP_USER_AGENT', '')
    if 'MSIE' in user_agent:
        filename = quote(filename)
        request.response.setHeader(
            "Content-disposition", 'attachment; filename=%s' % filename)

    else:
        request.response.setHeader(
            "Content-disposition", 'attachment; filename="%s"' % filename)


def hide_fields_from_behavior(form, fieldnames):
    """Hide fields defined in behaviors.
    """
    for group in form.groups:
        for fieldname in fieldnames:
            if fieldname in group.fields:
                group.fields[fieldname].mode = HIDDEN_MODE


def omit_classification_group(form):
    for group in form.groups:
        if group.__name__ == u'classification':
            form.groups.remove(group)
