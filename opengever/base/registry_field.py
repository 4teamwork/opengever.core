from plone.registry.field import DisallowedProperty
from plone.registry.field import InterfaceConstrainedProperty
from plone.registry.field import PersistentField
from plone.registry.field import StubbornProperty
from plone.registry.interfaces import IPersistentField
from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import ITime
import zope.schema


class Time(PersistentField, zope.schema.Time):
    pass


@implementer(IPersistentField)
@adapter(ITime)
def persistentFieldAdapter(context):
    """Turn a non-persistent field into a persistent one
    We overwrite plone.registry.fieldfactory.persistentFieldAdapter just for
    the Time field, which does not have a persistent equivalent in plone's
    registry.
    """

    if IPersistentField.providedBy(context):
        return context

    # Begin of customization
    persistent_class = Time
    # End of customization

    if not issubclass(persistent_class, context.__class__):
        __traceback_info__ = "Can only clone a field of an equivalent type."
        return None

    ignored = list(DisallowedProperty.uses + StubbornProperty.uses)
    constrained = list(InterfaceConstrainedProperty.uses)

    instance = persistent_class.__new__(persistent_class)

    context_dict = dict(
        [(k, v) for k, v in context.__dict__.items() if k not in ignored]
    )

    for key, iface in constrained:
        value = context_dict.get(key, None)
        if value is None or value == context.missing_value:
            continue
        value = iface(value, None)
        if value is None:
            __traceback_info__ = (
                "The property `{0}` cannot be adapted to "
                "`{1}`.".format(key, iface.__identifier__,)
            )
            return None
        context_dict[key] = value

    instance.__dict__.update(context_dict)
    return instance
