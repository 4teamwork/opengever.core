from opengever.base.utils import make_nonpersistent
from opengever.base.utils import make_persistent
from opengever.propertysheets.exceptions import BadCustomPropertiesFactoryConfiguration
from opengever.propertysheets.field import IPropertySheetField
from persistent.dict import PersistentDict
from persistent.mapping import PersistentMapping
from plone.behavior.annotation import AnnotationsFactoryImpl
from plone.behavior.annotation import AnnotationStorage
from plone.behavior.interfaces import ISchemaAwareFactory
from zope.interface import alsoProvides


def deep_update(dict_, otherdict):
    for k, v in otherdict.iteritems():
        if isinstance(v, (dict, PersistentMapping)):
            dict_[k] = deep_update(dict_.get(k, {}), v)
        else:
            dict_[k] = v
    return dict_


class CustomPropertiesStorageImpl(AnnotationsFactoryImpl):
    """Storage for custom properties in content annotations.

    Custom properties are actual property values on content for schemas
    defined in property sheets.

    Does not replace existing property sheet values when they are set, but
    instead accumulate all values. Values can only be cleared programmatically
    with the `clear` method.
    """
    CUSTOM_PROPERTIES_NAME = 'custom_properties'

    def __init__(self, context, schema):
        # These are safeguards against bad configuration for the moment.
        if schema.names() != [self.CUSTOM_PROPERTIES_NAME]:
            raise BadCustomPropertiesFactoryConfiguration(
                u"Custom properties factory must be assigned to a schema "
                u"with only a '{}' field.".format(
                    self.CUSTOM_PROPERTIES_NAME
                )
            )

        field = schema[self.CUSTOM_PROPERTIES_NAME]
        if not IPropertySheetField.providedBy(field):
            raise BadCustomPropertiesFactoryConfiguration(
                u"The schema must contain a field providing "
                u"'IPropertySheetField'"
            )

        super(CustomPropertiesStorageImpl, self).__init__(context, schema)

    def __getattr__(self, name):
        """Convert persistent data structures to non-persistent ones.
        """
        return make_nonpersistent(
            super(CustomPropertiesStorageImpl, self).__getattr__(name)
        )

    def get_plain_values(self, name):
        return super(CustomPropertiesStorageImpl, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name not in self.__dict__['schema']:
            super(CustomPropertiesStorageImpl, self).__setattr__(name, value)
        else:
            prefixed_name = self.__dict__['prefix'] + name
            if value is None:
                # Early return if the value is `None`, but make sure to
                # initialize annotations with `None` as this is expected by the
                # default value patches.
                if prefixed_name not in self.__dict__['annotations']:
                    self.__dict__['annotations'][prefixed_name] = None
                return

            # for not `None` values always validate type first
            if not isinstance(value, (dict, PersistentDict)):
                raise TypeError(
                    "Only 'dict' or 'PersistentDict' values are allowed."
                )

            new_value = make_persistent(value)
            value_to_update = self.__dict__['annotations'].get(prefixed_name)
            # we could have an initial stored value of `None`
            if value_to_update is None:
                value_to_update = PersistentDict()

            deep_update(value_to_update, new_value)

            self.__dict__['annotations'][prefixed_name] = value_to_update

    def clear(self):
        """Clear all custom properties."""
        prefixed_name = self.__dict__['prefix'] + self.CUSTOM_PROPERTIES_NAME
        if prefixed_name in self.__dict__['annotations']:
            del self.__dict__['annotations'][prefixed_name]


class CustomPropertiesStorage(AnnotationStorage):
    """Behavior adapter factory for storing custom properties."""

    def __call__(self, context):
        return CustomPropertiesStorageImpl(context, self.schema)


alsoProvides(CustomPropertiesStorage, ISchemaAwareFactory)
