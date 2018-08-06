"""
These are convenience helpers to address z3c.form's shortcomings, since
there's no built in way to

- retrieve groups by their name (only by index)
- retrieve fields in groups by their canonical name

without iterating over all the groups and fields.
"""

from plone.z3cform.fieldsets.interfaces import IGroupFactory
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IGroupForm
import logging


log = logging.getLogger('opengever.base.formutils')


class FormUtilsError(Exception):
    pass


def collect_fields_by_name(form):
    fields_by_name = {}

    def extract_fields(fields_obj):
        for fn, field in fields_obj.items():
            if fn in fields_by_name:
                raise FormUtilsError('Ambigious field name: %r' % fn)
            fields_by_name[fn] = field

    if not IForm.providedBy(form):
        raise FormUtilsError('Not an IForm: %r' % form)

    extract_fields(form.fields)

    if IGroupForm.providedBy(form):
        for group in form.groups:
            extract_fields(group.fields)

    return fields_by_name


def field_by_name(form, name):
    """Retrieve a field in a z3c.form, even if it's in a group.

    Returns `None` if field doesn't exist / can't be found.

    It will not do a recursive lookup. Group forms could in theory contain
    further group forms. This function doesn't consider those, it only looks
    at a single level of groups.

    The `name` must be the canonical internal name of the z3c.form field. For
    fields in the base schema, this is simply the name of the zope.schema
    field. For fields in behavior schemas, this is the name of the behavior
    schema class and the field name joined with a dot.

    Examples:

    >>> field_by_name(form, 'message')
    >>> field_by_name(form, 'IOGmail.title')
    """
    fields_by_name = collect_fields_by_name(form)
    return fields_by_name.get(name)


def omit_field_by_name(form, name):
    """Omit a field by name.
    """
    # Make sure field name is unambiguous
    collect_fields_by_name(form)

    if name in form.fields:
        form.fields = form.fields.omit(name)

    if IGroupForm.providedBy(form):
        for group in form.groups:
            if name in group.fields:
                group.fields = group.fields.omit(name)


def hide_field_by_name(form, name):
    """Hide a field by name.
    """
    fields_by_name = collect_fields_by_name(form)
    field = fields_by_name.get(name)
    if field:
        field.mode = HIDDEN_MODE


def group_by_name(form, name):
    """Retrieve a z3c.form group by name.

    Returns `None` if no such Group exists, or raises an error if the form
    isn't a group form.
    """
    if not IGroupForm.providedBy(form):
        raise FormUtilsError('Not an IGroupForm: %r' % form)

    for group in form.groups:
        if group.__name__ == name:
            return group


def collect_widgets_by_name(form):
    widgets_by_name = {}

    def extract_widgets(widgets_obj):
        for wn, widget in widgets_obj.items():
            if wn in widgets_by_name:
                raise FormUtilsError('Ambigious widget name: %r' % wn)
            widgets_by_name[wn] = widget

    if not IForm.providedBy(form):
        raise FormUtilsError('Not an IForm: %r' % form)

    extract_widgets(form.widgets)

    if IGroupForm.providedBy(form):
        for group in form.groups:
            if IGroupFactory.providedBy(group):
                msg = (
                    "Unexpectedly found GroupFactory instead of Group "
                    "in form.groups for %r" % form
                )
                log.error('')
                log.error(msg)
                log.error(
                    "This usually means you attempted to use widget_by_name() "
                    "in an earlier method than form.update() (like "
                    "updateWidgets or updateFields. This won't work because "
                    "GroupFactories will only get instantiated in "
                    "z3c.form.group.Group.update(), and only after that will "
                    "their widgets be present / ready."
                )
                log.error('')
                raise FormUtilsError(msg)
            extract_widgets(group.widgets)

    return widgets_by_name


def widget_by_name(form, name):
    widgets_by_name = collect_widgets_by_name(form)
    return widgets_by_name.get(name)
