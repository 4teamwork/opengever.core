from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


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
