from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import Choice
from zope.schema import getFieldsInOrder
import json


@implementer(ISerializeToJson)
@adapter(PropertySheetSchemaDefinition, Interface)
class SerializePropertySheetSchemaDefinitionToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kwargs):
        definition = self.context

        serialized_definition = {
            'id': definition.name,
            'fields': [],
            'assignments': definition.assignments,
        }
        docprops = self.get_docprops_for_schema()

        for name, field in getFieldsInOrder(definition.schema_class):
            ps_field = {
                'name': name,
                'field_type': self.get_field_type(field),
                'title': field.title,
                'description': field.description,
                'required': field.required,
                'available_as_docproperty': name in docprops,
                'read_group': self.context.read_group_mapping.get(name),
                'write_group': self.context.write_group_mapping.get(name),
            }

            ps_field.update(self.get_values(field))
            ps_field.update(self.get_defaults(field))

            serialized_definition['fields'].append(ps_field)

        return json_compatible(serialized_definition)

    def get_docprops_for_schema(self):
        storage = PropertySheetSchemaStorage()
        definition = storage.get(self.context.name)
        return definition.docprops

    def get_field_type(self, field):
        """Return propertysheet field_type name given a zope.schema field.
        """
        type_map = {
            v.fieldcls.__name__: k for k, v
            in PropertySheetSchemaDefinition.FACTORIES.items()
        }
        return type_map[field.__class__.__name__]

    def get_values(self, field):
        values = {}
        vocab = getattr(field, 'vocabulary', None)

        value_type = getattr(field, 'value_type', None)
        if isinstance(value_type, Choice):
            vocab = value_type.vocabulary

        if vocab:
            values['values'] = [t.value for t in vocab]

        return values

    def get_defaults(self, field):
        """Determine static or dynamic defaults.
        """
        defaults = {}

        # Order is important here.
        # default_from_member is internally turned into a default_expression,
        # which in turn is implemented as a default-factory-factory.
        # Therefore these must be checked in exactly this order.
        if getattr(field, 'default_from_member', None) is not None:
            defaults['default_from_member'] = json.loads(field.default_from_member)
        elif getattr(field, 'default_expression', None) is not None:
            defaults['default_expression'] = field.default_expression
        elif getattr(field, 'defaultFactory', None) is not None:
            defaults['default_factory'] = dottedname(field.defaultFactory)

        else:
            # Only check for a default if none of the dynamic defaults
            # above are present. Otherwise .default might be a property
            # that invokes a factory, and we would then accidentally
            # materialize that dynamic default and serialize is as a
            # static one.
            if field.default is not None:
                defaults['default'] = field.default

        return defaults
