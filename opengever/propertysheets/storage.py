from opengever.propertysheets.definition import PropertySheetSchemaDefinition
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
        schema_definition._save(storage)

    def get(self, name):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})

        if name not in storage:
            return None

        return PropertySheetSchemaDefinition._load(storage, name)
