from ftw.testbrowser import browsing
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
             '@vocabularies/classification_classification_vocabulary'))
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

    def _get_schema_fieldset(self, schema, name):
        for item in schema['fieldsets']:
            if item['behavior'] == name:
                return item
        return None

    def assert_translated_title_fields(self, response, required_languages, inactive_languages):
        fieldset = self._get_schema_fieldset(response, "plone")
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
