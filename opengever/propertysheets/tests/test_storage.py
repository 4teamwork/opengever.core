from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing.test_case import FunctionalTestCase
from plone.supermodel import loadString
from plone.supermodel import serializeSchema
from zope.annotation import IAnnotations


class TestPropertySheetSchemaStorage(FunctionalTestCase):

    def test_save_schema_definition(self):
        definition = PropertySheetSchemaDefinition.create("myschema")
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)

        storage = PropertySheetSchemaStorage(self.portal)
        storage.save(definition)

        annotations = IAnnotations(self.portal)
        self.assertIn(
            "opengever.propertysheets.schema_definitions", annotations
        )
        storage = annotations["opengever.propertysheets.schema_definitions"]
        self.assertIn("myschema", storage)
        self.assertEqual(
            storage["myschema"],
            serializeSchema(definition.schema_class, name="myschema"),
        )
        deserialized = loadString(storage["myschema"])
        self.assertIn("myschema", deserialized.schemata)

    def test_get_inexistent_schema_definition(self):
        storage = PropertySheetSchemaStorage(self.portal)
        self.assertIsNone(storage.get("idontexist"))

    def test_get_schema_definition(self):
        storage = PropertySheetSchemaStorage(self.portal)
        definition = PropertySheetSchemaDefinition.create("myschema")
        storage.save(definition)

        loaded = storage.get("myschema")
        self.assertEqual("myschema", loaded.name)

    def test_list_empty_storage(self):
        storage = PropertySheetSchemaStorage(self.portal)
        self.assertEqual([], storage.list())

    def test_list_definitions(self):
        storage = PropertySheetSchemaStorage(self.portal)
        definition1 = PropertySheetSchemaDefinition.create("schema1")
        definition1.add_field("bool", u"yesorno", u"y/n", u"", False)

        definition2 = PropertySheetSchemaDefinition.create("schema2")
        definition2.add_field("bool", u"yesorno", u"y/n", u"", False)

        storage.save(definition1)
        storage.save(definition2)

        self.assertItemsEqual(
            ["schema1", "schema2"], [each.name for each in storage.list()]
        )
