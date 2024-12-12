from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from jsonschema import Draft4Validator
from opengever.testing import IntegrationTestCase
from plone import api


class TestSchemaEndpoint(IntegrationTestCase):

    def setUp(self):
        super(TestSchemaEndpoint, self).setUp()
        self.lang_tool = api.portal.get_tool('portal_languages')

    @browsing
    def test_schema_endpoint_id_for_vocabulary(self, browser):
        self.login(self.regular_user, browser)
        url = self.document.absolute_url() + '/@schema'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json
        expected_url = "/".join(
            (self.document.absolute_url(),
             '@sources/classification'))
        self.assertEqual(
            expected_url,
            response['properties']['classification']['vocabulary']['@id']
        )

    @browsing
    def test_schema_endpoint_id_for_querysource(self, browser):
        self.login(self.regular_user, browser)
        url = self.document.absolute_url() + '/@schema'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json
        expected_url = "/".join(
            (self.document.absolute_url(),
             '@querysources/keywords'))
        self.assertEqual(
            expected_url,
            response['properties']['keywords']['items']['querysource']['@id']
            )

    @browsing
    def test_add_schema_only_contains_translated_title_fields_for_active_languages(self, browser):
        self.login(self.regular_user, browser)

        self.lang_tool.supported_langs = ['de']
        response = browser.open(
            self.leaf_repofolder, view='@schema/opengever.repository.repositoryfolder',
            method='GET',
            headers=self.api_headers,
        ).json
        self.assert_translated_title_fields(
            response, required_languages=['de'], inactive_languages=['fr', 'en'])

        self.lang_tool.supported_langs = ['fr', 'en']
        response = browser.open(
            self.leaf_repofolder, view='@schema/opengever.repository.repositoryfolder',
            method='GET',
            headers=self.api_headers,
        ).json
        self.assert_translated_title_fields(
            response, required_languages=['fr', 'en'], inactive_languages=['de'])

    @browsing
    def test_add_schema_does_not_contain_protected_fields(self, browser):
        self.login(self.regular_user, browser)
        response = browser.open(
            self.leaf_repofolder, view='@schema/opengever.dossier.businesscasedossier',
            method='GET',
            headers=self.api_headers,
        ).json
        fieldset = self._get_schema_fieldset(response, "classification")
        self.assertIn('classification', fieldset['fields'])
        self.assertIn('privacy_layer', fieldset['fields'])

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        response = browser.open(
            self.leaf_repofolder, view='@schema/opengever.dossier.businesscasedossier',
            method='GET',
            headers=self.api_headers,
        ).json
        fieldset = self._get_schema_fieldset(response, "classification")
        self.assertNotIn('classification', fieldset['fields'])
        self.assertNotIn('privacy_layer', fieldset['fields'])

    @browsing
    def test_add_schema_does_contain_protected_fields_if_display_mode(self, browser):
        self.login(self.regular_user, browser)
        response = browser.open(
            self.leaf_repofolder, view='@schema/opengever.dossier.businesscasedossier',
            method='GET',
            headers=self.api_headers,
        ).json
        fieldset = self._get_schema_fieldset(response, "classification")
        self.assertIn('classification', fieldset['fields'])
        self.assertIn('privacy_layer', fieldset['fields'])

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        response = browser.open(
            self.leaf_repofolder,
            view='@schema/opengever.dossier.businesscasedossier?mode=display',
            method='GET',
            headers=self.api_headers,
        ).json
        fieldset = self._get_schema_fieldset(response, "classification")
        self.assertIn('classification', fieldset['fields'])
        self.assertIn('privacy_layer', fieldset['fields'])

    @browsing
    def test_edit_schema_only_contains_translated_title_fields_for_active_languages(self, browser):
        self.login(self.regular_user, browser)

        self.lang_tool.supported_langs = ['de']
        response = browser.open(
            self.leaf_repofolder, view='@schema',
            method='GET',
            headers=self.api_headers,
        ).json
        self.assert_translated_title_fields(
            response, required_languages=['de'], inactive_languages=['fr', 'en'])

        self.lang_tool.supported_langs = ['fr', 'en']
        response = browser.open(
            self.leaf_repofolder, view='@schema',
            method='GET',
            headers=self.api_headers,
        ).json
        self.assert_translated_title_fields(
            response, required_languages=['fr', 'en'], inactive_languages=['de'])

    @browsing
    def test_edit_schema_does_not_contain_protected_fields(self, browser):
        self.login(self.regular_user, browser)
        response = browser.open(
            self.leaf_repofolder, view='@schema',
            method='GET',
            headers=self.api_headers,
        ).json
        fieldset = self._get_schema_fieldset(response, "classification")
        self.assertIn('classification', fieldset['fields'])
        self.assertIn('privacy_layer', fieldset['fields'])

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        response = browser.open(
            self.leaf_repofolder, view='@schema',
            method='GET',
            headers=self.api_headers,
        ).json
        fieldset = self._get_schema_fieldset(response, "classification")
        self.assertNotIn('classification', fieldset['fields'])
        self.assertNotIn('privacy_layer', fieldset['fields'])

    @browsing
    def test_edit_schema_sets_display_mode_for_responsible_field_when_necessary(self, browser):
        self.login(self.dossier_responsible, browser)
        response = browser.open(
            self.dossier, view='@schema', method='GET',
            headers=self.api_headers,).json
        self.assertNotIn('mode', response['properties']["responsible"])

        self.activate_feature('grant_role_manager_to_responsible')
        response = browser.open(
            self.dossier, view='@schema', method='GET',
            headers=self.api_headers,).json
        self.assertIn('mode', response['properties']["responsible"])
        self.assertEqual("display", response['properties']["responsible"]['mode'])

        self.dossier.give_permissions_to_responsible()
        response = browser.open(
            self.dossier, view='@schema', method='GET',
            headers=self.api_headers,).json
        self.assertNotIn('mode', response['properties']["responsible"])

    @browsing
    def test_schema_endpoint_returns_jsonschema_for_propertysheets(self, browser):
        """This just tests that the @schema endpoint returns JSON schemas
        for propertysheets at all.

        Detailed tests for how the JSON schemas are constructed for complex
        sheets can be found in opengever.propertysheets.tests.test_schema
        """
        self.login(self.regular_user, browser)

        sheet_id = 'example'
        sheet = create(
            Builder("property_sheet_schema")
            .named(sheet_id)
            .assigned_to_slots(u"IDossier.dossier_type.businesscase")
            .with_field("int", u"number", u"A number", u"", True)
        )

        browser.open(
            view='@schema/virtual.propertysheet.%s' % sheet_id,
            method='GET',
            headers=self.api_headers,
        )

        json_schema = sheet.get_json_schema()
        Draft4Validator.check_schema(json_schema)
        self.assertEqual(browser.json, json_schema)

    def _get_schema_fieldset(self, schema, name):
        for item in schema['fieldsets']:
            if item['id'] == name:
                return item
        return None

    def assert_translated_title_fields(self, response, required_languages, inactive_languages):
        fieldset = self._get_schema_fieldset(response, "common")
        for lang in required_languages:
            field_name = 'title_{}'.format(lang)
            self.assertIn(field_name, response['required'])
            self.assertIn(field_name, response['properties'])
            self.assertIn(field_name, fieldset['fields'])

        for lang in inactive_languages:
            field_name = 'title_{}'.format(lang)
            self.assertNotIn(field_name, response['required'])
            self.assertNotIn(field_name, response['properties'])
            self.assertNotIn(field_name, fieldset['fields'])
