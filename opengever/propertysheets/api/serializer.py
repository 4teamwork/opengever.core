from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFieldsInOrder


@implementer(ISerializeToJson)
@adapter(PropertySheetSchemaDefinition, Interface)
class SerializePropertySheetSchemaDefinitionToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kwargs):
        definition = self.context
        schema = definition.schema_class

        data = {
            'id': definition.name,
            'fields': [],
            'assignments': definition._assignments,
        }

        FIELD_TYPE_TO_TYPE_NAME = {
            v.fieldcls.__name__: k for k, v
            in PropertySheetSchemaDefinition.FACTORIES.items()
        }

        for name, schema_field in getFieldsInOrder(schema):
            field = {}
            field['name'] = name
            field['field_type'] = FIELD_TYPE_TO_TYPE_NAME[schema_field.__class__.__name__]
            field['title'] = schema_field.title
            field['description'] = schema_field.description
            field['required'] = schema_field.required

            vocab = None
            if field['field_type'] == 'choice':
                vocab = getattr(schema_field, 'vocabulary', None)

            elif field['field_type'] == 'multiple_choice':
                vocab = schema_field.value_type.vocabulary

            if vocab:
                field['values'] = [t.value for t in vocab]

            if schema_field.default:
                field['default'] = schema_field.default

            # field['default_factory'] = name
            # field['default_expression'] = name
            # field['default_from_member'] = name
            data['fields'].append(field)

        return data
