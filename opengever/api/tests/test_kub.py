from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPClientError
from ftw.testbrowser.exceptions import HTTPServerError
from opengever.kub.testing import KUB_RESPONSES
from opengever.kub.testing import KuBIntegrationTestCase
from plone import api
import requests_mock


@requests_mock.Mocker()
class TestKubEndpoint(KuBIntegrationTestCase):

    @browsing
    def test_handles_errors_raised_by_remote_service(self, mocker, browser):
        browser.exception_bubbling = True
        self.login(self.regular_user, browser)

        def assertErrorHandling(tested_error_code, raised_error_code, raised_http_exception, error_message):
            self.mock_get_full_entity_by_id(
                mocker, self.person_julie, status_code=tested_error_code)

            with self.assertRaises(raised_http_exception):
                browser.open(api.portal.get(),
                             view='/@kub/{}'.format(self.person_julie),
                             method='GET',
                             headers=self.api_headers)

            self.assertEqual(
                raised_error_code,
                browser.status_code,
                '{} should raise a {}'.format(tested_error_code, raised_error_code))
            self.assertEqual(
                tested_error_code,
                browser.json.get('service_error').get('status_code'),
                'The service_error status code should contain the original status code')
            self.assertEqual(error_message,
                             browser.json.get('message'))

        assertErrorHandling(tested_error_code=404,
                            raised_error_code=404,
                            raised_http_exception=HTTPClientError,
                            error_message=u'Contact was not found in KuB.')

        assertErrorHandling(tested_error_code=408,
                            raised_error_code=504,
                            raised_http_exception=HTTPServerError,
                            error_message=u'Error while communicating with KuB')

        assertErrorHandling(tested_error_code=500,
                            raised_error_code=502,
                            raised_http_exception=HTTPServerError,
                            error_message=u'Error while communicating with KuB')

        assertErrorHandling(tested_error_code=502,
                            raised_error_code=502,
                            raised_http_exception=HTTPServerError,
                            error_message=u'Error while communicating with KuB')

        assertErrorHandling(tested_error_code=504,
                            raised_error_code=504,
                            raised_http_exception=HTTPServerError,
                            error_message=u'Error while communicating with KuB')

    @browsing
    def test_proxies_to_corresponding_kub_endpoint(self, mocker, browser):
        self.login(self.regular_user, browser)
        self.mock_get_full_entity_by_id(mocker, self.person_julie)
        browser.open(api.portal.get(),
                     view='/@kub/{}'.format(self.person_julie),
                     method='GET',
                     headers=self.api_headers)

        uid = self.person_julie.split(":")[1]
        url = "{}people/{}".format(self.client.kub_api_url, uid)
        self.assertEqual(KUB_RESPONSES[url], browser.json)
