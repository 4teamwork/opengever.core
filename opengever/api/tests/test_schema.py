from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api


class TestSchemaEndpoint(IntegrationTestCase):

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
    def test_add_schema_only_contains_title_de_by_default(self, browser):
        self.login(self.regular_user, browser)
        response = browser.open(
            self.leaf_repofolder, view='@schema/opengever.repository.repositoryfolder',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertIn('title_de', response['required'])
        self.assertNotIn('title_fr', response['required'])
        self.assertIn('title_de', response['properties'])
        self.assertNotIn('title_fr', response['properties'])

        fieldset = self._get_schema_fieldset(response, "plone")
        self.assertIn('title_de', fieldset['fields'])
        self.assertNotIn('title_fr', fieldset['fields'])

    @browsing
    def test_edit_schema_only_contains_title_de_by_default(self, browser):
        self.login(self.regular_user, browser)
        response = browser.open(
            self.leaf_repofolder, view='@schema',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertIn('title_de', response['required'])
        self.assertNotIn('title_fr', response['required'])
        self.assertIn('title_de', response['properties'])
        self.assertNotIn('title_fr', response['properties'])

        fieldset = self._get_schema_fieldset(response, "plone")
        self.assertIn('title_de', fieldset['fields'])
        self.assertNotIn('title_fr', fieldset['fields'])

    @browsing
    def test_add_schema_also_contains_title_fr_when_lang_is_enabled(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('fr-ch')

        self.login(self.regular_user, browser)
        response = browser.open(
            self.leaf_repofolder, view='@schema/opengever.repository.repositoryfolder',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertIn('title_de', response['required'])
        self.assertIn('title_fr', response['required'])
        self.assertIn('title_de', response['properties'])
        self.assertIn('title_fr', response['properties'])

        fieldset = self._get_schema_fieldset(response, "plone")
        self.assertIn('title_de', fieldset['fields'])
        self.assertIn('title_fr', fieldset['fields'])

    @browsing
    def test_edit_schema_also_contains_title_fr_when_lang_is_enabled(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('fr-ch')

        self.login(self.regular_user, browser)
        response = browser.open(
            self.leaf_repofolder, view='@schema',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertIn('title_de', response['required'])
        self.assertIn('title_fr', response['required'])
        self.assertIn('title_de', response['properties'])
        self.assertIn('title_fr', response['properties'])

        fieldset = self._get_schema_fieldset(response, "plone")
        self.assertIn('title_de', fieldset['fields'])
        self.assertIn('title_fr', fieldset['fields'])

    def _get_schema_fieldset(self, schema, name):
        for item in schema['fieldsets']:
            if item['behavior'] == name:
                return item
        return None
