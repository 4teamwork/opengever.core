from ftw.builder import builder_registry
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage


class PropertySheetSchemaBuilder(object):
    """Create a property sheet schema definition and persist it in storage."""
    def __init__(self, session):
        self.session = session
        self.arguments = {
            'name': 'schema',
            'assignments': None,
            'docprops': []
        }
        self.field_defs = []
        self.storage = PropertySheetSchemaStorage()

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def named(self, name):
        self.arguments['name'] = name
        return self

    def assigned_to_slots(self, *args):
        self.arguments['assignments'] = args
        return self

    def with_simple_boolean_field(self):
        return self.with_field("bool", u"yesorno", u"y/n", u"", True)

    def with_simple_textline_field(self):
        return self.with_field(
            "textline", u"shorttext", u"Text", u"Say something.", True
        )

    def with_field(self, field_type, name, title, description, required,
                   values=None, default=None, default_factory=None,
                   default_expression=None, default_from_member=None,
                   available_as_docproperty=False):
        if available_as_docproperty:
            self.arguments['docprops'].append(name)
        self.field_defs.append(
            (field_type, name, title, description, required, values,
             default, default_factory, default_expression, default_from_member)
        )
        return self

    def create(self, **kwargs):
        definition = PropertySheetSchemaDefinition.create(
            self.arguments['name'],
            self.arguments['assignments'],
            self.arguments['docprops']
        )
        for field_def in self.field_defs:
            definition.add_field(*field_def)
        self.storage.save(definition)
        return self.storage.get(definition.name)


builder_registry.register('property_sheet_schema', PropertySheetSchemaBuilder)
