from ftw.testbrowser import browsing
from opengever.kub.interfaces import IKuBSettings
from opengever.kub.testing import KUB_RESPONSES
from opengever.kub.testing import KuBIntegrationTestCase
from plone import api
from zExceptions import NotFound
import json
import requests_mock


@requests_mock.Mocker()
class TestKubEndpoint(KuBIntegrationTestCase):

    @browsing
    def test_handles_errors_raised_by_remote_service(self, mocker, browser):
        browser.exception_bubbling = True
        self.login(self.regular_user, browser)

        def assertErrorHandling(tested_error_code):
            self.mock_get_by_id(
                mocker, self.person_julie, status_code=tested_error_code)

            with self.assertRaises(NotFound):
                browser.open(api.portal.get(),
                             view='/@kub/{}'.format(self.person_julie),
                             method='GET',
                             headers=self.api_headers)

        assertErrorHandling(tested_error_code=404)

        assertErrorHandling(tested_error_code=408)

        assertErrorHandling(tested_error_code=500)

        assertErrorHandling(tested_error_code=502)

        assertErrorHandling(tested_error_code=504)

    @browsing
    def test_serializes_additional_ui_attributes(self, mocker, browser):
        api.portal.set_registry_record(
            name='additional_ui_attributes', interface=IKuBSettings,
            value=[u'age', u'department'])
        self.login(self.regular_user, browser)
        self.mock_get_by_id(mocker, self.person_julie)
        browser.open(api.portal.get(),
                     view='/@kub/{}'.format(self.person_julie),
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual([u'age', u'department'], browser.json['additional_ui_attributes'])

    @browsing
    def test_proxies_to_corresponding_kub_endpoint(self, mocker, browser):
        self.login(self.regular_user, browser)
        self.mock_get_by_id(mocker, self.person_julie)
        browser.open(api.portal.get(),
                     view='/@kub/{}'.format(self.person_julie),
                     method='GET',
                     headers=self.api_headers)

        url = "{}resolve/{}".format(self.client.kub_api_url, self.person_julie)
        expected_data = json.loads(json.dumps(KUB_RESPONSES[url]))
        expected_data['additional_ui_attributes'] = []
        self.assertEqual(expected_data, browser.json)
