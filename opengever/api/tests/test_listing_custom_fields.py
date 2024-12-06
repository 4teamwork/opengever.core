from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase


class TestListingCustomFieldsGet(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_listing_custom_fields_fixture_slots(self, browser):
        self.login(self.manager)
        create(
            Builder("property_sheet_schema")
            .named("default_doc_schema")
            .assigned_to_slots(u"IDocument.default")
            .with_field("textline", u"f1", u"Field 1", u"", False)
        )

        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@listing-custom-fields',
                     headers=self.api_headers)

        self.assertEqual(
            {
                u"documents": {
                    u"properties": {
                        u"choose_custom_field_string": {
                            u"name": u"choose_custom_field_string",
                            u"title": u"Choose",
                            u'widget': None,
                            u"type": u"string"
                        },
                        u'choosemulti_custom_field_strings': {
                            u'name': u'choosemulti_custom_field_strings',
                            u'title': u'Choose multi',
                            u'widget': None,
                            u'type': u'array'
                        },
                        u"f1_custom_field_string": {
                            u"name": u"f1_custom_field_string",
                            u"title": u"Field 1",
                            u'widget': None,
                            u"type": u"string"
                        },
                        u'date_custom_field_date': {
                            u'name': u'date_custom_field_date',
                            u'title': u'Choose a date',
                            u'widget': u'date',
                            u'type': u'string'
                        },
                        u"num_custom_field_int": {
                            u"name": u"num_custom_field_int",
                            u"title": u"Number",
                            u'widget': None,
                            u"type": u"integer"
                        },
                        u"textline_custom_field_string": {
                            u"name": u"textline_custom_field_string",
                            u"title": u"A line of text",
                            u'widget': None,
                            u"type": u"string"
                        },
                        u"yesorno_custom_field_boolean": {
                            u"name": u"yesorno_custom_field_boolean",
                            u"title": u"Yes or no",
                            u'widget': None,
                            u"type": u"boolean"
                        }
                    }
                },
                u"dossiers": {
                    u"properties": {
                        u'additional_title_custom_field_string': {
                            u'name': u'additional_title_custom_field_string',
                            u'title': u'Additional dossier title',
                            u'type': u'string',
                            u'widget': None
                        },
                        u'choose_dossier_custom_field_string': {
                            u'name': u'choose_dossier_custom_field_string',
                            u'title': u'Choose',
                            u'type': u'string',
                            u'widget': None
                        },
                        u'choosemulti_dossier_custom_field_strings': {
                            u'name': u'choosemulti_dossier_custom_field_strings',
                            u'title': u'Choose multi',
                            u'type': u'array',
                            u'widget': None
                        },

                        u'date_dossier_custom_field_date': {
                            u'name': u'date_dossier_custom_field_date',
                            u'title': u'Choose a date',
                            u'type': u'string',
                            u'widget': u'date'
                        },
                        u'location_custom_field_string': {
                            u'name': u'location_custom_field_string',
                            u'title': u'Location',
                            u'type': u'string',
                            u'widget': None
                        },
                        u'num_dossier_custom_field_int': {
                            u'name': u'num_dossier_custom_field_int',
                            u'title': u'Number',
                            u'type': u'integer',
                            u'widget': None
                        },

                        u'yesorno_dossier_custom_field_boolean': {
                            u'name': u'yesorno_dossier_custom_field_boolean',
                            u'title': u'Yes or no',
                            u'type': u'boolean',
                            u'widget': None
                        }
                    }
                }
            },
            browser.json
        )

    @browsing
    def test_listing_custom_fields_merges_duplicate_slots(self, browser):
        self.login(self.manager)
        PropertySheetSchemaStorage().clear()

        create(
            Builder("property_sheet_schema")
            .named("schema2")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"Y/N (question)", u"", True)
        )
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.regulations")
            .with_field("bool", u"yesorno", u"Y/N (regulations)", u"", True)
        )

        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@listing-custom-fields',
                     headers=self.api_headers)

        self.assertEqual(
            {
                u"documents": {
                    u"properties": {
                        u"yesorno_custom_field_boolean": {
                            u"name": u"yesorno_custom_field_boolean",
                            u"title": u"Y/N (regulations)",
                            u"type": u"boolean",
                            u"widget": None
                        }
                    }
                }
            },
            browser.json
        )
