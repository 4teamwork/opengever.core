from opengever.propertysheets.exportimport import dottedname
from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import iter_fields
from zope.globalrequest import getRequest
import json


def get_jsonschema_for_propertysheet(sheet_id):
    # Avoid circular import
    from opengever.propertysheets.storage import PropertySheetSchemaStorage
    storage = PropertySheetSchemaStorage()

    schema_definition = storage.get(sheet_id)
    if schema_definition is None:
        raise KeyError(sheet_id)

    return schema_definition.get_json_schema()


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

        # Transform default *value* to *token*
        default = getattr(field.field, 'default', None)
        if default is not None:
            vocab = getattr(field.field, 'vocabulary', None)
            if vocab:
                term = vocab.getTerm(field.field.default)
                properties[name]['default'] = term.token

        # Determine required fields
        if field.field.required:
            required.append(name)

        # Serialize defaultFactory dottedname, if present
        default_factory = field.field.defaultFactory
        if default_factory is not None:
            properties[name]['default_factory'] = dottedname(default_factory)

        # Serialize default_expression, if present
        default_expression = getattr(field.field, 'default_expression', None)
        if default_expression is not None:
            properties[name]['default_expression'] = default_expression

        # Serialize default_from_member options, if present
        default_from_member = getattr(field.field, 'default_from_member', None)
        if default_from_member is not None:
            properties[name]['default_from_member'] = json.loads(default_from_member)

    schema_info = {
        "type": "object",
        "title": schema_class.getName(),
        "properties": IJsonCompatible(properties),
        "fieldsets": get_fieldset_infos(fieldsets),
    }
    if required:
        schema_info["required"] = required

    return schema_info
