from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
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

        used_assignments = set()
        for definition_data in storage.values():
            used_assignments.update(definition_data['assignments'])

        for new_assignment in schema_definition.assignments:
            if new_assignment in used_assignments:
                raise InvalidSchemaAssignment(
                    u"The assignment '{}' is already in use.".format(
                        new_assignment)
                )
            used_assignments.add(new_assignment)

        schema_definition._save(storage)

    def get(self, name):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})

        if name not in storage:
            return None

        return PropertySheetSchemaDefinition._load(storage, name)

    def query(self, assignment):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})
        for name, definition_data in storage.items():
            if assignment in definition_data['assignments']:
                return self.get(name)

        return None
