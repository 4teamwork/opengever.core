from opengever.propertysheets.field import IPropertySheetField
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IChoice


@implementer(IFieldSerializer)
@adapter(IPropertySheetField, IDexterityContent, Interface)
class PropertySheetFieldSerializer(DefaultFieldSerializer):
    """Make sure choice fields are serialized correctly.

    We can't reuse `IFieldSerializer` adapters for the property sheet schema as
    they attempt to retrieve the current value from context.
    Instead we directly implement support for choice fields and provide correct
    serialization of terms by duplicating the `ChoiceFieldSerializer` term
    serialization.
    Serialization for all other permitted field types is already handled
    correctly by the call to `json_compatible` in `DefaultFieldSerializer`.
    """
    def get_value(self, default=None):
        value = super(PropertySheetFieldSerializer, self).get_value(
            default=default
        )
        return self.serialize_custom_properties(value)

    def serialize_custom_properties(self, value):
        """Serialize nested custom property field data structure to JSON.

        Handles invalid data grafecully and returns it, whenever possible.
        """
        # something is weird, be grafecul
        if not isinstance(value, dict):
            return value

        for slot_name, data in value.items():
            definition = PropertySheetSchemaStorage().query(slot_name)
            # the sheet definition no longer exist, be graceful
            if not definition:
                continue

            # the value is not a dict, be graceful
            if not isinstance(data, dict):
                continue

            for name, field in definition.get_fields():
                if name not in data:
                    continue

                if IChoice.providedBy(field):
                    field_value = data[name]
                    try:
                        term = field.vocabulary.getTerm(field_value)
                        data[name] = {"token": term.token, "title": term.title}
                    except LookupError:
                        # in case of invalid terms we pretend that there is no
                        # value in storage and drop the field from serialization
                        del data[name]

                elif hasattr(field, 'value_type') and IChoice.providedBy(
                        field.value_type):
                    field_values = data[name]
                    tokenized_values = []
                    for field_value in field_values:
                        try:
                            term = field.value_type.vocabulary.getTerm(field_value)
                            tokenized_values.append({"token": term.token, "title": term.title})
                        except LookupError:
                            # In case of invalid terms we skip them and pretend there
                            # is no such value
                            pass

                    data[name] = tokenized_values

        return value
