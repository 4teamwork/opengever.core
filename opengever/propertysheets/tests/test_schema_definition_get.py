from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.propertysheets.testing import dummy_default_factory_fr
from opengever.testing import IntegrationTestCase
from plone import api


class TestSchemaDefinitionGet(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_property_sheet_schema_definition_get_empty_list(self, browser):
        self.login(self.regular_user, browser)
        PropertySheetSchemaStorage().clear()

        browser.open(
            view="@propertysheets", method="GET", headers=self.api_headers
        )
        self.assertEqual(
            {
                u"items": [],
                u"@id": u"http://nohost/plone/@propertysheets",
            },
            browser.json,
        )

    @browsing
    def test_property_sheet_schema_definition_get_list(self, browser):
        self.login(self.regular_user, browser)

        browser.open(
            view="@propertysheets", method="GET", headers=self.api_headers
        )
        self.assertEqual(
            {
                u"@id": u"http://nohost/plone/@propertysheets",
                u"items": [
                    {
                        u"@id": u"http://nohost/plone/@propertysheets/schema2",
                        u"@type": "virtual.propertysheet",
                        u"id": "schema2",
                    },
                    {
                        u"@id": u"http://nohost/plone/@propertysheets/schema1",
                        u"@type": "virtual.propertysheet",
                        u"id": "schema1",
                    },
                    {
                        u"@id": u"http://nohost/plone/@propertysheets/dossier_default",
                        u"@type": "virtual.propertysheet",
                        u"id": "dossier_default",
                    },
                ],
            },
            browser.json,
        )

    @browsing
    def test_property_sheet_schema_definition_get_sheet_schema(self, browser):
        self.login(self.regular_user, browser)

        choices = ["one", "two", "three"]
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"y/n", u"", False)
            .with_field(
                "choice", u"chooseone", u"choose", u"", False, values=choices
            )
        )

        browser.open(
            view="@propertysheets/schema",
            method="GET",
            headers=self.api_headers,
        )

        self.assertEqual(
            {
                u"assignments": [u"IDocumentMetadata.document_type.question"],
                u"fields": [
                    {
                        u"description": u"",
                        u"field_type": u"bool",
                        u"name": u"yesorno",
                        u"required": False,
                        u"title": u"y/n",
                    },
                    {
                        u"description": u"",
                        u"field_type": u"choice",
                        u"name": u"chooseone",
                        u"required": False,
                        u"title": u"choose",
                        u"values": [u"one", u"two", u"three"],
                    },
                ],
                u"id": u"schema",
            },
            browser.json,
        )
        self.assertEqual("application/json", browser.mimetype)

    @browsing
    def test_property_sheet_schema_definition_get_field_with_static_default(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocument.default")
            .with_field("choice", u"language", u"Language", u"", True,
                        values=choices, default=u'fr')
        )

        browser.open(
            view="@propertysheets/schema",
            method="GET",
            headers=self.api_headers,
        )

        field = browser.json['fields'][0]
        self.assertEqual(u'fr', field['default'])

    @browsing
    def test_property_sheet_schema_definition_get_field_with_default_factory(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocument.default")
            .with_field("choice", u"language", u"Language", u"", True,
                        values=choices,
                        default_factory=dottedname(dummy_default_factory_fr))
        )

        browser.open(
            view="@propertysheets/schema",
            method="GET",
            headers=self.api_headers,
        )

        field = browser.json['fields'][0]
        self.assertNotIn('default', field)
        self.assertEqual(
            dottedname(dummy_default_factory_fr),
            field['default_factory'])

    @browsing
    def test_property_sheet_schema_definition_get_field_with_default_expression(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocument.default")
            .with_field("choice", u"language", u"Language", u"", True,
                        values=choices,
                        default_expression="portal/language")
        )

        browser.open(
            view="@propertysheets/schema",
            method="GET",
            headers=self.api_headers,
        )

        field = browser.json['fields'][0]
        self.assertNotIn('default', field)
        self.assertEqual(
            'portal/language',
            field['default_expression'])

    @browsing
    def test_property_sheet_schema_definition_get_field_with_default_from_member(self, browser):
        self.login(self.regular_user, browser)

        member = api.user.get_current()
        member.setProperties({'location': 'CH'})

        choices = [u'CH', u'DE', u'US']
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocument.default")
            .with_field("choice", u"location", u"Location", u"", True,
                        values=choices,
                        default_from_member={'property': 'location'})
        )

        browser.open(
            view="@propertysheets/schema",
            method="GET",
            headers=self.api_headers,
        )

        field = browser.json['fields'][0]
        self.assertNotIn('default', field)
        self.assertEqual(
            {'property': 'location'},
            field['default_from_member'])

    @browsing
    def test_property_sheet_schema_definition_get_404(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            browser.open(
                view="@propertysheets/idonotexist",
                method="GET",
                headers=self.api_headers
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Sheet 'idonotexist' not found.",
                "type": "NotFound",
            },
            browser.json,
        )

    @browsing
    def test_property_sheet_schema_definition_get_too_many_path_segments(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo/bar",
                method="GET",
                headers=self.api_headers
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Must supply either zero or one parameters.",
                "type": "BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_anonymous_cannot_get_property_sheets(self, browser):
        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets",
                method="GET",
                headers=self.api_headers
            )
