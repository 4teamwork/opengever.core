from plone.app.dexterity.behaviors.metadata import MetadataBase
from Products.CMFCore.interfaces import ISiteRoot
from zope.schema.interfaces import ValidationError


NO_VALUE_FOUND = object()


def acquire_field_value(field, container):
    if isinstance(container, MetadataBase) or container is None:
        # These are odd cases where we get passed a weird context and can't
        # (or don't want to) acquire an actual value.
        return NO_VALUE_FOUND

    obj = container
    while not ISiteRoot.providedBy(obj):
        try:
            interface_ = field.interface
        except AttributeError:
            pass
        else:
            try:
                adpt = interface_(obj)
            except TypeError:
                # could not adapt
                pass
            else:
                # XXX: Potential for infinite recursion here (Issue #2033)
                value = field.get(adpt)
                try:
                    field.validate(value)
                    return value
                except ValidationError:
                    pass

        obj = obj.aq_inner.aq_parent
    return NO_VALUE_FOUND


def set_default_with_acquisition(field, default=None):
    """Sets a default value generator which uses the value
    from the parent object, if existing, otherwise it uses
    the given default value.
    """
    def default_value_generator(data):
        container = data.context

        acquired_value = acquire_field_value(field, container)
        if acquired_value is not NO_VALUE_FOUND:
            return acquired_value

        # otherwise use default value
        if default:
            # XXX: Use sentinel value (Issue #2029)
            return default
        else:
            # use first value
            try:
                return tuple(data.widget.terms)[0].value
            except AttributeError:
                return None

    return default_value_generator
