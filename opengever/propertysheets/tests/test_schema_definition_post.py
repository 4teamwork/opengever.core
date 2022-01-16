from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.propertysheets.testing import dummy_default_factory_42
from opengever.propertysheets.testing import dummy_default_factory_fr
from opengever.propertysheets.testing import dummy_default_factory_gruen
from opengever.propertysheets.testing import dummy_default_factory_some_text
from opengever.propertysheets.testing import dummy_default_factory_some_text_line
from opengever.propertysheets.testing import dummy_default_factory_true
from opengever.testing import IntegrationTestCase
from plone import api
from zope import schema
import json


class TestSchemaDefinitionPost(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_property_sheet_schema_definition_post_defaults(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "text"}]}
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )
        storage = PropertySheetSchemaStorage()
        self.assertEqual(4, len(storage))
        definition = storage.get("question")

        self.assertEqual("question", definition.name)
        schema_class = definition.schema_class

        self.assertEqual(["foo"], schema_class.names())
        field = schema_class["foo"]
        self.assertIsInstance(field, schema.Text)
        self.assertEqual(
            u"foo", field.title, "Expected title to default to name"
        )
        self.assertEqual(u"", field.description)
        self.assertFalse(field.required)

    @browsing
    def test_property_sheet_schema_definition_post(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "foo",
                    "field_type": "bool",
                    "title": u"Y/N",
                    "description": u"yes or no",
                    "required": True,
                }
            ],
            "assignments": [u"IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        self.assertEqual(
            {
                u"id": u"question",
                u"fields": [
                    {
                        u"description": u"yes or no",
                        u"field_type": u"bool",
                        u"name": u"foo",
                        u"required": True,
                        u"title": u"Y/N",
                    },
                ],
                u"assignments": [u"IDocumentMetadata.document_type.question"],
            },
            browser.json,
        )
        self.assertEqual("application/json", browser.mimetype)

        storage = PropertySheetSchemaStorage()
        self.assertEqual(4, len(storage))
        definition = storage.get("question")

        self.assertEqual("question", definition.name)
        self.assertEqual((u"IDocumentMetadata.document_type.question",),
                         definition.assignments)
        schema_class = definition.schema_class

        self.assertEqual(["foo"], schema_class.names())
        field = schema_class["foo"]
        self.assertIsInstance(field, schema.Bool)
        self.assertEqual(
            u"Y/N",
            field.title,
        )
        self.assertEqual(u"yes or no", field.description)
        self.assertTrue(field.required)

    @browsing
    def test_property_sheet_schema_definition_post_supports_all_field_types(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein"
                },
                {
                    "name": "wahl",
                    "field_type": u"choice",
                    "title": u"w\xe4hl was",
                    "values": [u"\xf6ins", u"zwei"]
                },
                {
                    "name": "colors",
                    "field_type": u"multiple_choice",
                    "title": u"Select one or more",
                    "values": [u"gr\xfcn", "blau", "weiss"]
                },
                {
                    "name": "nummer",
                    "field_type": u"int",
                    "title": u"zahl"
                },
                {
                    "name": "text",
                    "field_type": u"text",
                    "title": u"text",
                    "required": True
                },
                {
                    "name": "zeiletext",
                    "field_type": u"textline",
                    "title": u"zeile"
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(4, len(storage))
        definition = storage.get("meinschema")

        self.assertEqual(
            ["yn", "wahl", "colors", "nummer", "text", "zeiletext"],
            definition.get_fieldnames()
        )

    @browsing
    def test_property_sheet_schema_definition_post_supports_setting_static_defaults(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein",
                    "default": True,
                },
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Language",
                    "values": [u"de", u"fr", u"en"],
                    "default": u"fr",
                },
                {
                    "name": "colors",
                    "field_type": u"multiple_choice",
                    "title": u"Select one or more",
                    "values": [u"gr\xfcn", "blau", "weiss"],
                    "default": [u"gr\xfcn"],
                },
                {
                    "name": "nummer",
                    "field_type": u"int",
                    "title": u"zahl",
                    "default": 42,
                },
                {
                    "name": "text",
                    "field_type": u"text",
                    "title": u"text",
                    "required": True,
                    "default": u"some text",
                },
                {
                    "name": "zeiletext",
                    "field_type": u"textline",
                    "title": u"zeile",
                    "default": u"some text line",
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")
        fields = dict(definition.get_fields())

        self.assertEqual(True, fields['yn'].default)
        self.assertEqual(u'fr', fields['language'].default)
        self.assertEqual(set([u'gr\xfcn']), fields['colors'].default)
        self.assertEqual(42, fields['nummer'].default)
        self.assertEqual(u'some text', fields['text'].default)
        self.assertEqual(u'some text line', fields['zeiletext'].default)

    @browsing
    def test_property_sheet_schema_definition_post_supports_setting_default_factories(self, browser):
        # PropertySheetsManager is not allowed to modify dynamic defaults
        self.login(self.manager, browser)

        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein",
                    "default_factory": dottedname(dummy_default_factory_true),
                },
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Language",
                    "values": [u"de", u"fr", u"en"],
                    "default_factory": dottedname(dummy_default_factory_fr),
                },
                {
                    "name": "colors",
                    "field_type": u"multiple_choice",
                    "title": u"Select one or more",
                    "values": [u"gr\xfcn", "blau", "weiss"],
                    "default_factory": dottedname(dummy_default_factory_gruen),
                },
                {
                    "name": "nummer",
                    "field_type": u"int",
                    "title": u"zahl",
                    "default_factory": dottedname(dummy_default_factory_42),
                },
                {
                    "name": "text",
                    "field_type": u"text",
                    "title": u"text",
                    "required": True,
                    "default_factory": dottedname(dummy_default_factory_some_text),
                },
                {
                    "name": "zeiletext",
                    "field_type": u"textline",
                    "title": u"zeile",
                    "default_factory": dottedname(dummy_default_factory_some_text_line),
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")
        fields = dict(definition.get_fields())

        self.assertEqual(True, fields['yn'].default)
        self.assertEqual(dummy_default_factory_true,
                         fields['yn'].defaultFactory)

        self.assertEqual(u'fr', fields['language'].default)
        self.assertEqual(dummy_default_factory_fr,
                         fields['language'].defaultFactory)

        self.assertEqual(set([u'gr\xfcn']), fields['colors'].default)
        self.assertEqual(dummy_default_factory_gruen,
                         fields['colors'].defaultFactory)

        self.assertEqual(42, fields['nummer'].default)
        self.assertEqual(dummy_default_factory_42,
                         fields['nummer'].defaultFactory)

        self.assertEqual(u'Some text', fields['text'].default)
        self.assertEqual(dummy_default_factory_some_text,
                         fields['text'].defaultFactory)

        self.assertEqual(u'Some text line', fields['zeiletext'].default)
        self.assertEqual(dummy_default_factory_some_text_line,
                         fields['zeiletext'].defaultFactory)

    @browsing
    def test_property_sheet_schema_definition_post_supports_setting_default_expressions(self, browser):
        # PropertySheetsManager is not allowed to modify dynamic defaults
        self.login(self.manager, browser)

        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein",
                    "default_expression": "python: True",
                },
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Language",
                    "values": [u"de", u"fr", u"en"],
                    "default_expression": "python: u'fr'",
                },
                {
                    "name": "colors",
                    "field_type": u"multiple_choice",
                    "title": u"Select one or more",
                    "values": [u"gr\xfcn", "blau", "weiss"],
                    "default_expression": "python: {u'gr\\xfcn'}",
                },
                {
                    "name": "nummer",
                    "field_type": u"int",
                    "title": u"zahl",
                    "default_expression": "python: 42",
                },
                {
                    "name": "text",
                    "field_type": u"text",
                    "title": u"text",
                    "required": True,
                    "default_expression": "python: 'Some text'",
                },
                {
                    "name": "zeiletext",
                    "field_type": u"textline",
                    "title": u"zeile",
                    "default_expression": "python: 'Some text line'",
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")
        fields = dict(definition.get_fields())

        self.assertEqual(True, fields['yn'].default)
        self.assertEqual(True, fields['yn'].defaultFactory())
        self.assertEqual("python: True",
                         fields['yn'].default_expression)

        self.assertEqual(u'fr', fields['language'].default)
        self.assertEqual(u'fr', fields['language'].defaultFactory())
        self.assertEqual("python: u'fr'",
                         fields['language'].default_expression)

        self.assertEqual(set([u'gr\xfcn']), fields['colors'].default)
        self.assertEqual(set([u'gr\xfcn']), fields['colors'].defaultFactory())
        self.assertEqual(u"python: {u'gr\\xfcn'}",
                         fields['colors'].default_expression)

        self.assertEqual(42, fields['nummer'].default)
        self.assertEqual(42, fields['nummer'].defaultFactory())
        self.assertEqual("python: 42",
                         fields['nummer'].default_expression)

        self.assertEqual(u'Some text', fields['text'].default)
        self.assertEqual(u'Some text', fields['text'].defaultFactory())
        self.assertEqual("python: 'Some text'",
                         fields['text'].default_expression)

        self.assertEqual(u'Some text line', fields['zeiletext'].default)
        self.assertEqual(u'Some text line', fields['zeiletext'].defaultFactory())
        self.assertEqual("python: 'Some text line'",
                         fields['zeiletext'].default_expression)

    @browsing
    def test_property_sheet_schema_definition_post_supports_setting_default_from_member(self, browser):
        self.login(self.regular_user, browser)

        member = api.user.get_current()
        member.setProperties({
            'listed': True,
            'language': 'fr',
            'description': 'Some text\n Lorem Ipsum',
            'fullname': u'B\xe4rfuss K\xe4thi',
        })

        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein",
                    "default_from_member": {'property': 'listed'},
                },
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Location",
                    "values": [u"de", u"fr", u"en"],
                    "default_from_member": {'property': 'language'},
                },
                {
                    "name": "text",
                    "field_type": u"text",
                    "title": u"text",
                    "default_from_member": {'property': 'description'},
                },
                {
                    "name": "zeiletext",
                    "field_type": u"textline",
                    "title": u"zeile",
                    "default_from_member": {'property': 'fullname'},
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }

        # PropertySheetsManager is not allowed to modify dynamic defaults
        self.login(self.manager, browser)
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        self.login(self.regular_user, browser)
        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")
        fields = dict(definition.get_fields())

        self.assertEqual(True, fields['yn'].default)
        self.assertEqual(True, fields['yn'].defaultFactory())
        self.assertEqual('{"property": "listed"}',
                         fields['yn'].default_from_member)

        self.assertEqual(u'fr', fields['language'].default)
        self.assertEqual(u'fr', fields['language'].defaultFactory())
        self.assertEqual('{"property": "language"}',
                         fields['language'].default_from_member)

        self.assertEqual('Some text\n Lorem Ipsum', fields['text'].default)
        self.assertEqual('Some text\n Lorem Ipsum', fields['text'].defaultFactory())
        self.assertEqual('{"property": "description"}',
                         fields['text'].default_from_member)

        self.assertEqual(u'B\xe4rfuss K\xe4thi', fields['zeiletext'].default)
        self.assertEqual(u'B\xe4rfuss K\xe4thi', fields['zeiletext'].defaultFactory())
        self.assertEqual('{"property": "fullname"}',
                         fields['zeiletext'].default_from_member)

    @browsing
    def test_property_sheet_schema_definition_post_reject_invalid_choices(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "wahl",
                    "field_type": u"choice",
                    "title": u"w\xe4hl was",
                    "values": [1, True]
                }
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }

        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_replaces_existing_schema(self, browser):
        self.login(self.propertysheets_manager, browser)
        create(Builder("property_sheet_schema").named("question"))

        data = {
            "fields": [
                {
                    "name": "foo",
                    "field_type": "bool",
                    "title": u"Y/N",
                    "description": u"yes or no",
                    "required": True,
                }
            ],
        }
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(4, len(storage))
        definition = storage.get("question")

        self.assertEqual("question", definition.name)
        self.assertEqual(["foo"], definition.schema_class.names())

    @browsing
    def test_property_sheet_schema_definition_post_requires_valid_assignment(
        self, browser
    ):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [{"name": "foo", "field_type": "bool"}],
            "assignments": [u"fail"],
        }
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/invalidassignment",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"The assignment 'fail' is invalid.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_requires_unique_assignment(
        self, browser
    ):
        self.login(self.propertysheets_manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("fixture")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
        )

        data = {
            "fields": [{"name": "foo", "field_type": "bool"}],
            "assignments": [u"IDocumentMetadata.document_type.question"],
        }
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/invalidassignment",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"The assignment 'IDocumentMetadata.document_type."
                            "question' is already in use.",
                "type": "BadRequest",
            },
            browser.json,
        )
        storage = PropertySheetSchemaStorage()
        self.assertEqual(4, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_requires_name(
        self, browser
    ):
        self.login(self.propertysheets_manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "bool"}]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Missing parameter sheet_name.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_requires_valid_name(
        self, browser
    ):
        self.login(self.propertysheets_manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "bool"}]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/in-val.id",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"The name 'in-val.id' is invalid.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_requires_fields(
        self, browser
    ):
        self.login(self.propertysheets_manager, browser)

        data = {"fields": []}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Missing or invalid field definitions.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_requires_valid_fields_type(
        self, browser
    ):
        self.login(self.propertysheets_manager, browser)

        data = {"fields": {"foo": None}}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Missing or invalid field definitions.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_prevents_duplicate_field_name(
        self, browser
    ):
        self.login(self.propertysheets_manager, browser)

        dupe1 = {"name": "dupe", "field_type": "text"}
        dupe2 = {"name": "foo", "field_type": "text"}
        data = {"fields": [dupe1, dupe1, dupe2, dupe2]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Duplicate fields 'dupe', 'foo'.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_property_sheet_schema_definition_post_invalid_type(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "invalid"}]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/question",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )
        self.assertDictContainsSubset(
            {
                "type": "BadRequest",
            },
            browser.json,
        )
        storage = PropertySheetSchemaStorage()
        self.assertEqual(3, len(storage))

    @browsing
    def test_non_propertysheets_managers_cannot_post(self, browser):
        self.login(self.administrator, browser)

        data = {"fields": [{"name": "foo", "field_type": "text"}]}
        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/test",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

    @browsing
    def test_limited_admin_cannot_post_propertysheets(self, browser):
        self.login(self.limited_admin, browser)

        data = {"fields": [{"name": "foo", "field_type": "text"}]}
        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/test",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

    @browsing
    def test_dynamic_defaults_require_manager_role(self, browser):
        self.login(self.propertysheets_manager, browser)

        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/test",
                method="POST",
                data=json.dumps({
                    "fields": [{
                        "name": "foo",
                        "field_type": "text",
                        "default_factory": dottedname(
                            dummy_default_factory_fr),
                    }]
                }),
                headers=self.api_headers,
            )

        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/test",
                method="POST",
                data=json.dumps({
                    "fields": [{
                        "name": "foo",
                        "field_type": "text",
                        "default_expression": "member/getId",
                    }]
                }),
                headers=self.api_headers,
            )

        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/test",
                method="POST",
                data=json.dumps({
                    "fields": [{
                        "name": "foo",
                        "field_type": "text",
                        "default_from_member": {'property': 'fullname'},
                    }]
                }),
                headers=self.api_headers,
            )
