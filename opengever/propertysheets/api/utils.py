from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import iter_fields


def get_property_sheet_schema(context, request, schema_class):
    fieldsets = get_fieldsets(context, request, schema_class)
    properties = get_jsonschema_properties(context, request, fieldsets)

    required = []
    for field in iter_fields(fieldsets):
        name = field.field.getName()
        # Determine required fields
        if field.field.required:
            required.append(name)

    schema_info = {
        "id": schema_class.getName(),
        "properties": IJsonCompatible(properties),
        "required": required,
        "fieldsets": get_fieldset_infos(fieldsets),
    }

    return schema_info
