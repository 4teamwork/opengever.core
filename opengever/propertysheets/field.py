from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.schema import IJSONField
from plone.schema import JSONField
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema import ValidationError


class IPropertySheetField(IJSONField):
    pass


@implementer(IPropertySheetField)
class PropertySheetField(JSONField):
    """Handle custom properties and validate them against their corresponding
    property sheet schema.

    Expects custom properties to be provided as a nested data structure of the
    following format:
    {
        "<assignment_slot_name>": {
            "<field_name>": "<field value>",
        }
    }

    It makes the distinction between at most one mandatory property sheet
    schema and further optional property sheet schemas.
    A property sheet is considered mandatory when a property sheet is
    available in storage for the currently active assignment slot.

    - The mandatory property sheet schema is defined by context state.
      Currently this is coupled to the value of a vocabulary based field, e.g.
      `document_type`. Each value provides a so called assignment slot.
      Property sheets can be assigned to those slots. If a property sheet is
      assigned to such a slot, validation of the sheet is enforced.
    - The optional property sheet schemas are defines as all sheets that fill
      one of the slots provided by `valid_assignment_slots_factory`.
    """

    def __init__(
        self,
        request_key,
        attribute_name,
        assignemnt_prefix,
        valid_assignment_slots_factory,
        **kwargs
    ):
        self.request_key = request_key
        self.attribute_name = attribute_name
        self.assignemnt_prefix = assignemnt_prefix
        self.valid_assignment_slots_factory = valid_assignment_slots_factory

        super(PropertySheetField, self).__init__(**kwargs)

    def _validate(self, value):
        super(PropertySheetField, self)._validate(value)

        active_assignment_slot = self.get_active_assignment_slot()
        mandatory_sheet = self.get_mandatory_property_sheet(
            active_assignment_slot
        )
        self.validate_mandatory_property_sheet(
            value, active_assignment_slot, mandatory_sheet
        )
        self.validate_optional_property_sheets(
            value, mandatory_sheet
        )

    def get_active_assignment_slot(self):
        """Return assignment slot currently considered active."""
        request = getRequest()

        value_name = None
        if self.request_key in request:
            value_name = request.get(self.request_key)[0]
        elif self.context:
            value_name = getattr(self.context, self.attribute_name)

        if not value_name:
            return None

        return "{}.{}".format(self.assignemnt_prefix, value_name)

    def get_mandatory_property_sheet(self, active_assignment_slot):
        return PropertySheetSchemaStorage().query(active_assignment_slot)

    def validate_mandatory_property_sheet(
        self, value, active_assignment_slot, mandatory_sheet
    ):
        """Validate mandatory sheet, if available."""
        if mandatory_sheet is None:
            return
        if value is None:
            value = {}

        data = value.get(active_assignment_slot, {})
        mandatory_sheet.validate(data)

    def validate_optional_property_sheets(self, value, mandatory_sheet):
        """Validate schemas for optional sheets."""
        if value is None:
            value = {}

        valid_assignment_slots = set(self.valid_assignment_slots_factory())

        for assignment_slot_name in value:
            optional_sheet = PropertySheetSchemaStorage().query(
                assignment_slot_name
            )

            if optional_sheet is None:
                raise ValidationError(
                    u"Custom properties for '{}' supplied, but no such "
                    u"property sheet is defined.".format(assignment_slot_name)
                )

            if assignment_slot_name not in valid_assignment_slots:
                raise ValidationError(
                    u"The property sheet '{}' cannot be used in this "
                    u"context with assignment '{}'".format(
                        optional_sheet.name, assignment_slot_name
                    )
                )

            # we have already validated this schema, take a shortcut
            if optional_sheet == mandatory_sheet:
                continue

            optional_sheet.validate(value.get(assignment_slot_name))