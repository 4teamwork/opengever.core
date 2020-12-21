from persistent.mapping import PersistentMapping
from plone import api
from plone.supermodel import loadString
from plone.supermodel import serializeSchema
from zope.annotation import IAnnotations


KEY = 'opengever.propertysheets'


class PropertySheetSchemas(object):

    @classmethod
    def list(cls):
        annotations = IAnnotations(api.portal.get())

        for name in annotations.get(KEY, {}):
            yield cls.get(name)

    @classmethod
    def save(cls, name, schema_class):
        annotations = IAnnotations(api.portal.get())

        if KEY not in annotations:
            annotations[KEY] = PersistentMapping()

        storage = annotations[KEY]
        storage[name] = serializeSchema(schema_class, name=name)

    @classmethod
    def get(cls, name):
        annotations = IAnnotations(api.portal.get())
        storage = annotations.get(KEY, {})

        if name not in storage:
            return None

        serialized_schema = storage[name]
        model = loadString(serialized_schema, policy=u'propertysheets')
        schema_class = model.schemata[name]

        return schema_class
