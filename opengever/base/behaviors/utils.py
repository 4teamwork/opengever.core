from plone.namedfile.utils import get_contenttype
from urllib import quote
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IValue
from z3c.form.value import ComputedValue
from zope.component import getMultiAdapter
import re


def propagate_vocab_restrictions(container, event, restricted_fields, marker):

    def dottedname(field):
        return '.'.join((field.interface.__name__, field.__name__))

    changed_fields = []
    for desc in event.descriptions:
        for name in desc.attributes:
            changed_fields.append(name)

    fields_to_check = []
    for field in restricted_fields:
        if dottedname(field) in changed_fields:
            fields_to_check.append(field)

    if not fields_to_check:
        return

    children = container.portal_catalog(
        # XXX: Depth should not be limited (Issue #2027)
        path={'depth': 2,
              'query': '/'.join(container.getPhysicalPath())},
        object_provides=(marker.__identifier__,)
    )

    for child in children:
        obj = child.getObject()
        for field in fields_to_check:
            voc = field.bind(obj).source
            value = field.get(field.interface(obj))
            if value not in voc:
                # obj, request, form, field, widget
                default = getMultiAdapter((
                    obj.aq_inner.aq_parent,
                    obj.REQUEST,
                    None,
                    field,
                    None,
                ), IValue, name='default')
                if isinstance(default, ComputedValue):
                    default = default.get()
                field.set(field.interface(obj), default)


# Used as sortkey for sorting strings in numerical order
# TODO: Move to a more suitable place
def split_string_by_numbers(x):
    x = str(x)
    r = re.compile('(\d+)')
    l = r.split(x)
    return [int(y) if y.isdigit() else y for y in l]


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
