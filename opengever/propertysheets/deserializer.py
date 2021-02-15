from opengever.propertysheets.field import IPropertySheetField
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IFieldDeserializer)
@adapter(IPropertySheetField, IDexterityContent, IBrowserRequest)
class PropertySheetFieldDeserializer(DefaultFieldDeserializer):
    """Delegate deserialization to property sheet fields."""

    def __call__(self, value):
        value = self.deserialize_custom_properties(value)
        return super(PropertySheetFieldDeserializer, self).__call__(value)

    def deserialize_custom_properties(self, value):
        """Use property sheet schema fields for deserialization, if a property
        sheet is found.

        Deserialization is very permissive with unknown values, but they will
        cause validation errors later in field validation.
        """
        if not isinstance(value, dict):
            return value

        for slot_name, data in value.items():
            definition = PropertySheetSchemaStorage().query(slot_name)
            if not definition:
                continue

            if not isinstance(data, dict):
                continue

            for name, field in definition.get_fields():
                if name not in data:
                    continue

                field_value = data[name]
                deserializer = getMultiAdapter(
                    (field, self.context, self.request), IFieldDeserializer
                )
                data[name] = deserializer(field_value)

        return value
