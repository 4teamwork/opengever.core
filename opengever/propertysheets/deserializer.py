from opengever.propertysheets.field import IPropertySheetField
from opengever.propertysheets.helpers import add_current_value_to_allowed_terms
from opengever.propertysheets.helpers import is_choice_field
from opengever.propertysheets.helpers import is_multiple_choice_field
from opengever.propertysheets.interfaces import IDuringPropertySheetFieldDeserialization
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import Set


@implementer(IFieldDeserializer)
@adapter(IPropertySheetField, IDexterityContent, IBrowserRequest)
class PropertySheetFieldDeserializer(DefaultFieldDeserializer):
    """Delegate deserialization to property sheet fields."""

    def __call__(self, value):
        alsoProvides(self.request, IDuringPropertySheetFieldDeserialization)
        self.request.context = self.context
        value = self.deserialize_custom_properties(value)
        resp = super(PropertySheetFieldDeserializer, self).__call__(value)
        noLongerProvides(self.request, IDuringPropertySheetFieldDeserialization)
        return resp

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

                # If an API client specifies None as the field value
                # for a multiple_choice field, the CollectionFieldDeserializer
                # will turn it into [None] which will cause RequiredMissing.
                # We therefore replace it with an empty list.
                if isinstance(field, Set) and field_value is None:
                    field_value = []

                if is_choice_field(field) or is_multiple_choice_field(field):
                    add_current_value_to_allowed_terms(field, self.context)

                data[name] = deserializer(field_value)

        return value
