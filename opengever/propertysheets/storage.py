from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidSchemaIdentifier
from persistent.mapping import PersistentMapping
from plone import api
from zope.annotation import IAnnotations


class PropertySheetSchemaStorage(object):
    """Handle storage and lookup of property sheets.

    Property sheets are stored in the annotation of the plone site.
    """
    ANNOTATIONS_KEY = 'opengever.propertysheets.schema_definitions'

    def __init__(self, context=None):
        self.context = context or api.portal.get()

    def list(self):
        annotations = IAnnotations(self.context)

        result = []
        for name in annotations.get(self.ANNOTATIONS_KEY, {}):
            result.append(self.get(name))
        return result

    def save(self, schema_definition):
        annotations = IAnnotations(self.context)

        if self.ANNOTATIONS_KEY not in annotations:
            annotations[self.ANNOTATIONS_KEY] = PersistentMapping()

        storage = annotations[self.ANNOTATIONS_KEY]

        used_identifiers = set()
        for definition_data in storage.values():
            used_identifiers.update(definition_data['identifiers'])

        for new_identifier in schema_definition.identifiers:
            if new_identifier in used_identifiers:
                raise InvalidSchemaIdentifier(
                    u"The identifier '{}' is already in use.".format(
                        new_identifier)
                )

        schema_definition._save(storage)

    def get(self, name):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})

        if name not in storage:
            return None

        return PropertySheetSchemaDefinition._load(storage, name)

    def query(self, identifier):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})
        for name, definition_data in storage.items():
            if identifier in definition_data['identifiers']:
                return self.get(name)

        return None
