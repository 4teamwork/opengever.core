from plone.app.dexterity.behaviors.metadata import MetadataBase
from Products.CMFCore.interfaces import ISiteRoot
from zope.schema.interfaces import ValidationError


NO_VALUE_FOUND = object()


def acquire_field_value(field, container):
    """Acquire a value for a particular field from an object's container or
    its closest ancestor.

    This works similar to Zope's Acquisition, but also supports fields in
    behaviors with AnnotationStorage.

    The strategy for acquiring a field value can be described as follows:

    - Find the closest ancestor that:
        - Supports the field in question (intermediate ancestors that
          don't support the field are skipped)
        - Has a value for the field that validates
    - If no such ancestor can be found, return the NO_VALUE_FOUND sentinel
    """
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
    """Factory to provide a default value by acquiring it from parents.

    First this function will attempt to acquire a value for the given field
    by walking up the chain of parents. If no value can be found via
    acuisition, we fall back on the provided static `default`, if given.

    If no static `default` value was given, the first term from the field's
    vocabulary will be used.
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


def set_default_with_acquisition_context_aware(field, default=None):
    """Sets a default value generator which uses the value
    from the parent object, if existing, otherwise it uses
    the given default value.
    """
    def default_value_generator(context):
        container = context

        acquired_value = acquire_field_value(field, container)
        if acquired_value is not NO_VALUE_FOUND:
            return acquired_value

        # otherwise use default value
        if default:
            # XXX: Use sentinel value (Issue #2029)
            return default
        else:
            # use first value
            return None

    return default_value_generator
