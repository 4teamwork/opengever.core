from opengever.base.schemadump.json_schema_helper import JSONSchema
from opengever.propertysheets.metaschema import IPropertySheetDefinition
from plone.restapi.services import Service
from plone.restapi.services.types.get import check_security
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder
from zope.schema import Object
import json


class PropertysheetMetaSchemaGet(Service):

    def reply(self):
        check_security(self.context)
        self.content_type = "application/json+schema"
        builder = JSONSchemaBuilder(
            IPropertySheetDefinition, self.context, self.request)
        schema = builder.build_schema().serialize()
        return schema

    def render(self):
        """Override plone.restapi's render() method to set sort_keys=False.

        This avoids our intended order, according to nested OrderedDicts,
        from being destroyed, and makes the schema much more human readable.
        """
        self.check_permission()
        content = self.reply()
        self.request.response.setHeader("Content-Type", self.content_type)
        return json.dumps(
            content, indent=2, sort_keys=False, separators=(", ", ": ")
        )


class JSONSchemaBuilder(object):
    """Builds a JSON Schema that describes propertysheet definitions.

    The bulk of the work is being done by IJsonSchemaProviders, many of them
    from plone.restapi, and some custom ones.

    This custom builder therefore mainly assembles the schema in the way we
    want it for the propertysheets metaschema, and does some cleanup to keep
    it readable, and easier to test.
    """

    KEYS_TO_DROP = ('factory', 'additionalItems')
    VOCAB_KEYS = ('enum', 'enumNames', 'choices')

    def __init__(self, zope_schema, context, request):
        self.zope_schema = zope_schema
        self.context = context
        self.request = request
        self.schema = None

    def build_schema(self):
        self.schema = JSONSchema(
            title='Propertysheet Meta Schema',
            additional_properties=False,
        )

        field_order = []
        for name, field in getFieldsInOrder(self.zope_schema):
            field_order.append(name)
            prop_def = self.build_property_definition(field)
            self.schema.add_property(name, prop_def, required=field.required)

        self.schema.set_field_order(field_order)
        return self.schema

    def build_property_definition(self, field):
        schema_provider = getMultiAdapter(
            (field, self.context, self.request),
            IJsonSchemaProvider,
        )

        prop_def = schema_provider.get_schema()

        # Set required fields for "Object" fields (i.e., nested dicts)
        value_type = getattr(field, 'value_type', None)
        if isinstance(value_type, Object):
            for nested_name, nested_field in getFieldsInOrder(value_type.schema):
                if nested_field.required:
                    if 'required' not in prop_def['items']:
                        prop_def['items']['required'] = []
                    prop_def['items']['required'].append(nested_name)

        self.clean_property_definition(prop_def)
        prop_def['additionalProperties'] = False

        items = prop_def.get('items')
        if items:
            self.clean_items(items)
            self.drop_redundant_vocabulary(prop_def['items'])

        return prop_def

    def clean_items(self, items):
        self.drop_unwanted_keys(items)

        # Title and description make no sense for item definitions
        items.pop('description', None)
        items.pop('title', None)

        item_props = items.get('properties', {})
        for prop_name in item_props:
            self.clean_property_definition(item_props[prop_name])

    def clean_property_definition(self, prop_def):
        self.drop_unwanted_keys(prop_def)
        self.drop_redundant_vocabulary(prop_def)

    def drop_redundant_vocabulary(self, dct):
        """We want to inline all the vocabularies for this schema.

        But sometimes plone.restapi still puts in (incorrectly constructed)
        vocabulary URLs. We remove those here.
        """
        if all([key in dct for key in self.VOCAB_KEYS]):
            dct.pop('vocabulary', None)

    def drop_unwanted_keys(self, dct):
        """Drop some noisy properties that aren't relevant for us.
        """
        for unwanted_key in self.KEYS_TO_DROP:
            dct.pop(unwanted_key, None)
