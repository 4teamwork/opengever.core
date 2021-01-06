from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import iter_fields
from zope.globalrequest import getRequest


def get_property_sheet_schema(schema_class):
    context = None
    request = getRequest()

    fieldsets = get_fieldsets(context, request, schema_class)
    properties = get_jsonschema_properties(context, request, fieldsets)
    # sanitize properties, prevent invalid vocabulary/source `@id`s
    for property in properties.itervalues():
        property.pop('vocabulary', None)
        property.pop('querysource', None)

    required = []
    for field in iter_fields(fieldsets):
        name = field.field.getName()
        # Determine required fields
        if field.field.required:
            required.append(name)

    schema_info = {
        "type": "object",
        "title": schema_class.getName(),
        "properties": IJsonCompatible(properties),
        "fieldsets": get_fieldset_infos(fieldsets),
    }
    if required:
        schema_info["required"] = required

    return schema_info
