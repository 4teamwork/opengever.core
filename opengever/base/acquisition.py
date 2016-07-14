from plone.app.dexterity.behaviors.metadata import MetadataBase
from Products.CMFCore.interfaces import ISiteRoot
from zope.schema.interfaces import ValidationError


NO_VALUE_FOUND = object()


def acquire_field_value(field, container):
    if isinstance(container, MetadataBase) or container is None:
        # we do not test the factory, it is not acquisition wrapped and
        # we cant get the request...
        return None

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
                value = field.get(adpt)
                try:
                    field.validate(value)
                    return value
                except ValidationError:
                    pass

        obj = obj.aq_inner.aq_parent
    return NO_VALUE_FOUND
