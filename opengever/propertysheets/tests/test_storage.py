from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing.test_case import FunctionalTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.supermodel import loadString
from plone.supermodel import serializeSchema
from zope.annotation import IAnnotations


class TestPropertySheetSchemaStorage(FunctionalTestCase):

    def test_save_schema_definition(self):
        definition = PropertySheetSchemaDefinition.create(
            "myschema",
            assignments=[u"IDocumentMetadata.document_type.question"]
        )
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)

        storage = PropertySheetSchemaStorage()
        storage.save(definition)

        annotations = IAnnotations(self.portal)
        self.assertIn(
            "opengever.propertysheets.schema_definitions", annotations
        )
        serialized = annotations["opengever.propertysheets.schema_definitions"]
        self.assertIsInstance(serialized, PersistentMapping)
        self.assertIn("myschema", serialized)
        self.assertEqual(
            serialized["myschema"]["schema"],
            serializeSchema(definition.schema_class, name="myschema")
        )
        self.assertIsInstance(
            serialized["myschema"]["assignments"], PersistentList
        )
        self.assertEqual(
            [u"IDocumentMetadata.document_type.question"],
            serialized["myschema"]["assignments"]
        )
        deserialized = loadString(serialized["myschema"]["schema"])
        self.assertIn("myschema", deserialized.schemata)

    def test_get_inexistent_schema_definition(self):
        storage = PropertySheetSchemaStorage()
        self.assertIsNone(storage.get("idontexist"))

    def test_get_schema_definition(self):
        storage = PropertySheetSchemaStorage()
        definition = PropertySheetSchemaDefinition.create("myschema")
        storage.save(definition)

        loaded = storage.get("myschema")
        self.assertEqual("myschema", loaded.name)

    def test_list_empty_storage(self):
        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    def test_list_definitions(self):
        storage = PropertySheetSchemaStorage()
        definition1 = PropertySheetSchemaDefinition.create("schema1")
        definition1.add_field("bool", u"yesorno", u"y/n", u"", False)

        definition2 = PropertySheetSchemaDefinition.create("schema2")
        definition2.add_field("bool", u"yesorno", u"y/n", u"", False)

        storage.save(definition1)
        storage.save(definition2)

        self.assertItemsEqual(
            ["schema1", "schema2"], [each.name for each in storage.list()]
        )

    def test_storage_len_empty(self):
        storage = PropertySheetSchemaStorage()
        self.assertEqual(0, len(storage))

    def test_storage_len_with_definitions(self):
        storage = PropertySheetSchemaStorage()
        definition1 = PropertySheetSchemaDefinition.create("schema1")
        storage.save(definition1)

        self.assertEqual(1, len(storage))

        storage = PropertySheetSchemaStorage()
        definition2 = PropertySheetSchemaDefinition.create("schema2")
        storage.save(definition2)

        self.assertEqual(2, len(storage))

    def test_storage_is_falsy_when_empty(self):
        storage = PropertySheetSchemaStorage()
        self.assertFalse(storage)

    def test_storage_is_truthy_when_not_empty(self):
        storage = PropertySheetSchemaStorage()
        definition1 = PropertySheetSchemaDefinition.create("schema1")
        storage.save(definition1)

        self.assertTrue(storage)

    def test_prevents_duplicate_assignments(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[
                u"IDocumentMetadata.document_type.offer",
                u"IDocumentMetadata.document_type.report"
            ]
        )
        storage.save(fixture)

        conflict = PropertySheetSchemaDefinition.create(
            "conflict", assignments=[u"IDocumentMetadata.document_type.report"]
        )
        with self.assertRaises(InvalidSchemaAssignment) as cm:
            storage.save(conflict)

        exc = cm.exception
        self.assertEqual(
            u"The assignment 'IDocumentMetadata.document_type.report' "
            "is already in use.",
            exc.message
        )

    def test_prevents_self_conflicting_assignment(self):
        storage = PropertySheetSchemaStorage()
        conflict = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[
                u"IDocument.default",
                u"IDocumentMetadata.document_type.report"
            ]
        )
        with self.assertRaises(InvalidSchemaAssignment) as cm:
            storage.save(conflict)

        self.assertEqual(
            u"The assignments 'IDocument.default', "
            u"'IDocumentMetadata.document_type.report' cannot be used for "
            u"the same sheet.",
            cm.exception.message
        )

    def test_prevents_document_field_name_default_conflicts_with_type(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[u"IDocument.default"],
        )
        fixture.add_field("bool", u"yesorno", u"y/n", u"", False)
        storage.save(fixture)

        conflict = PropertySheetSchemaDefinition.create(
            "conflict",
            assignments=[u"IDocumentMetadata.document_type.report"]
        )
        conflict.add_field("bool", u"yesorno", u"y/n", u"", False)
        with self.assertRaises(InvalidSchemaAssignment) as cm:
            storage.save(conflict)

        exc = cm.exception
        self.assertEqual(
            u"Overlapping field names 'yesorno' in assignment "
            u"'IDocument.default'",
            exc.message
        )

    def test_prevents_document_field_name_type_conflicts_with_default(self):
        storage = PropertySheetSchemaStorage()
        fixture1 = PropertySheetSchemaDefinition.create(
            "fixture1",
            assignments=[u"IDocumentMetadata.document_type.report"]
        )
        fixture1.add_field("bool", u"yesorno", u"y/n", u"", False)
        storage.save(fixture1)
        fixture2 = PropertySheetSchemaDefinition.create(
            "fixture2",
            assignments=[u"IDocumentMetadata.document_type.question"]
        )
        fixture2.add_field("bool", u"yesorno", u"y/n", u"", False)
        storage.save(fixture2)

        conflict = PropertySheetSchemaDefinition.create(
            "conflict",
            assignments=[u"IDocument.default"],
        )
        conflict.add_field("bool", u"yesorno", u"y/n", u"", False)
        with self.assertRaises(InvalidSchemaAssignment) as cm:
            storage.save(conflict)

        exc = cm.exception
        self.assertEqual(
            u"Overlapping field names 'yesorno' in assignment "
            "'IDocumentMetadata.document_type.question'",
            exc.message
        )

    def test_prevents_dossier_field_name_default_conflicts_with_type(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[u"IDossier.default"],
        )
        fixture.add_field("textline", u"yesorno", u"blabla", u"", False)
        storage.save(fixture)

        conflict = PropertySheetSchemaDefinition.create(
            "conflict",
            assignments=[u"IDossier.dossier_type.businesscase"]
        )
        conflict.add_field("bool", u"yesorno", u"y/n", u"", False)
        with self.assertRaises(InvalidSchemaAssignment) as cm:
            storage.save(conflict)

        exc = cm.exception
        self.assertEqual(
            u"Overlapping field names 'yesorno' in assignment "
            u"'IDossier.default'",
            exc.message
        )

    def test_prevents_dossier_field_name_type_conflicts_with_default(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[u"IDossier.dossier_type.businesscase"]
        )
        fixture.add_field("bool", u"yesorno", u"y/n", u"", False)
        storage.save(fixture)

        conflict = PropertySheetSchemaDefinition.create(
            "conflict",
            assignments=[u"IDossier.default"],
        )
        conflict.add_field("int", u"yesorno", u"a number", u"", False)
        with self.assertRaises(InvalidSchemaAssignment) as cm:
            storage.save(conflict)

        exc = cm.exception
        self.assertEqual(
            u"Overlapping field names 'yesorno' in assignment "
            "'IDossier.dossier_type.businesscase'",
            exc.message
        )

    def test_query_for_schema_by_assignment(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[
                u"IDocumentMetadata.document_type.question",
                u"IDocumentMetadata.document_type.report"
            ]
        )
        storage.save(fixture)

        schema = storage.query(u"IDocumentMetadata.document_type.report")
        self.assertIsNotNone(schema)
        self.assertEqual("fixture", schema.name)

    def test_query_for_nonexistent_assignment(self):
        storage = PropertySheetSchemaStorage()
        self.assertIsNone(storage.query("foo"))

    def test_remove_nonexistent_sheet(self):
        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())
        storage.remove("nix")
        self.assertEqual([], storage.list())

    def test_remove_sheet(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create("removeme")
        storage.save(fixture)
        self.assertEqual(1, len(storage.list()))

        storage.remove("removeme")

        self.assertEqual([], storage.list())

    def test_containment(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create("imin")
        storage.save(fixture)

        self.assertIn('imin', storage)
        self.assertNotIn(None, storage)
        self.assertNotIn('foo', storage)

    def test_clear_storage(self):
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create("removeme")
        storage.save(fixture)
        self.assertEqual(1, len(storage.list()))

        storage.clear()

        self.assertEqual([], storage.list())
