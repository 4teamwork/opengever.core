from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.dossier.interfaces import IDossierParticipants
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase
from plone import api


class TestSystemInformation(IntegrationTestCase):

    @browsing
    def test_provided_information_keys(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)
        self.assertEqual([
            u'dossier_participation_roles',
            u'property_sheets',
        ], sorted(browser.json.keys()))

    @browsing
    def test_dossier_participation_roles(self, browser):
        self.login(self.manager, browser)
        api.portal.set_registry_record('primary_participation_roles', ['regard'], IDossierParticipants)

        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual([
            {
                u'active': True,
                u'token': u'final-drawing',
                u'primary': False,
                u'docproperty_key': {
                    u'organization': u'ogg.final-drawing.organization.*',
                    u'person': u'ogg.final-drawing.person.*'
                },
                u'title': u'Final signature'
            },
            {
                u'active': True,
                u'token': u'regard',
                u'primary': True,
                u'docproperty_key': {
                    u'organization': u'ogg.regard.organization.*',
                    u'person': u'ogg.regard.person.*'
                },
                u'title': u'For your information'
            },
            {
                u'active': True,
                u'token': u'participation',
                u'primary': False,
                u'docproperty_key': {
                    u'organization': u'ogg.participation.organization.*',
                    u'person': u'ogg.participation.person.*'
                },
                u'title': u'Participation'
            }
        ], browser.json.get('dossier_participation_roles'))

    @browsing
    def test_property_sheets(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual(
            [u'dossier_default', u'schema1', u'schema2'],
            sorted(browser.json.get('property_sheets').keys())
        )

        self.assertEqual({

            u'assignments': [{
                u'id': u'IDocumentMetadata.document_type.directive',
                u'title': u'Document (Type: Directive)'
            }],
            u'id': u'schema2',
            u'fields': [{
                u'field_type': u'textline',
                u'description': u'',
                u'title': u'A line of text',
                u'required': False,
                u'available_as_docproperty': False,
                u'name': u'textline'
            }]
        }, browser.json.get('property_sheets').get('schema2'))

    @browsing
    def test_property_sheet_fields_doc_property_key(self, browser):
        self.login(self.regular_user, browser)
        PropertySheetSchemaStorage().clear()
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDossier.dossier_type.businesscase")
            .with_field("bool", u"digital", u"Digital", u"", False, available_as_docproperty=True)
            .with_field("int", u"age", u"Age", u"", False, available_as_docproperty=True)
            .with_field("bool", u"checked", u"Checked", u"", False, available_as_docproperty=False)
        )
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual(
            sorted(['schema']),
            sorted(browser.json.get('property_sheets').keys())
        )

        self.assertEqual(
            {
                u'assignments': [
                    {
                        u'id': u'IDossier.dossier_type.businesscase',
                        u'title': u'Dossier (Type: Business case)'
                    }
                ],
                u'id': u'schema',
                u'fields': [
                    {
                        u'field_type': u'bool',
                        u'description': u'',
                        u'docproperty_key': u'ogg.dossier.cp.digital',
                        u'title': u'Digital',
                        u'required': False,
                        u'available_as_docproperty': True,
                        u'name': u'digital'
                    }, {
                        u'field_type': u'int',
                        u'description': u'',
                        u'docproperty_key': u'ogg.dossier.cp.age',
                        u'title': u'Age',
                        u'required': False,
                        u'available_as_docproperty': True,
                        u'name': u'age'
                    }, {
                        u'field_type': u'bool',
                        u'description': u'',
                        u'title': u'Checked',
                        u'required': False,
                        u'available_as_docproperty': False,
                        u'name': u'checked'
                    }
                ]
            }, browser.json.get('property_sheets').get('schema')
        )
