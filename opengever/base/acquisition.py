from opengever.base.default_values import get_persisted_value_for_field
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
                interface_(obj)
            except TypeError:
                # could not adapt
                pass
            else:
                value = get_persisted_value_for_field(obj, field)
                try:
                    field.validate(value)
                    return value
                except ValidationError:
                    pass

        obj = obj.aq_inner.aq_parent
    return NO_VALUE_FOUND


def acquired_default_factory(field, default=None):
    """Returns a factory that produces a default by trying to acquire the
    field value from it's ancestors, if possible.

    If we fail to acquire a default, use the given `default` value.

    If no default value was given, fall back to the field's vocabulary's
    first value.

    Finally, if the field doesn't have a vocabulary, we fall back to
    returning `None`.
    """
    def default_value_generator(context):
        container = context

        bound_field = field.bind(container)
        acquired_value = acquire_field_value(bound_field, container)
        if acquired_value is not NO_VALUE_FOUND:
            return acquired_value

        # otherwise use default value
        if default:
            # XXX: Use sentinel value (Issue #2029)
            return default
        else:
            # use first value from vocabulary
            try:
                vocab = field.bind(container).source
                first = list(vocab)[0].value
                return first
            except (IndexError, TypeError):
                return None

    return default_value_generator
