from base64 import b64encode
from base64 import urlsafe_b64encode
from datetime import datetime
from ftw.testbrowser import browsing
from opengever.document.document import Document
from opengever.document.versioner import Versioner
from opengever.sign.sign import Signer
from opengever.sign.token import InvalidToken
from opengever.testing import SolrIntegrationTestCase
from zExceptions import Forbidden
from zExceptions import Unauthorized
import json
import re
import requests_mock


FROZEN_NOW = datetime(2024, 2, 18, 15, 45)

DEFAULT_MOCK_RESPONSE = {
    'id': '1',
    'redirect_url': 'http://external.example.org/signing-requests/123',
}


class TestUploadSignedPdfPost(SolrIntegrationTestCase):

    features = ['sign']

    @browsing
    def test_raises_forbidden_if_context_is_not_in_signing_state(self, browser):
        with self.login(self.regular_user):
            url = self.document.absolute_url() + '/@upload-signed-pdf'

        browser.exception_bubbling = True
        with self.assertRaises(Forbidden):
            browser.open(url, method='POST', headers=self.api_headers)

    @browsing
    @requests_mock.Mocker()
    def test_access_token_is_required_in_payload(self, browser, mocker):
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        with self.login(self.regular_user, browser):
            browser.open(self.document.absolute_url() + '/@workflow/' + Document.draft_signing_transition,
                         method='POST',
                         headers=self.api_headers)

            url = self.document.absolute_url() + '/@upload-signed-pdf'

        with browser.expect_http_error(400):
            browser.open(url,
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'signed_pdf_data': '<data>'}))

        self.assertEqual(
            {'message': "Property 'access_token' is required",
             'type': 'BadRequest'},
            browser.json)

    @browsing
    @requests_mock.Mocker()
    def test_signed_pdf_data_is_required_in_payload(self, browser, mocker):
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        with self.login(self.regular_user, browser):
            browser.open(self.document.absolute_url() + '/@workflow/' + Document.draft_signing_transition,
                         method='POST',
                         headers=self.api_headers)

            url = self.document.absolute_url() + '/@upload-signed-pdf'

        with browser.expect_http_error(400):
            browser.open(url,
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'access_token': '<token>'}))

        self.assertEqual(
            {'message': "Property 'signed_pdf_data' is required",
             'type': 'BadRequest'},
            browser.json)

    @browsing
    @requests_mock.Mocker()
    def test_requires_a_valid_access_token(self, browser, mocker):
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        with self.login(self.regular_user, browser):
            browser.open(self.document.absolute_url() + '/@workflow/' + Document.draft_signing_transition,
                         method='POST',
                         headers=self.api_headers)

            url = self.document.absolute_url() + '/@upload-signed-pdf'

        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.open(url,
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'access_token': urlsafe_b64encode('<invalid-token>'),
                                          'signed_pdf_data': '<data>'}))

    @browsing
    @requests_mock.Mocker()
    def test_can_complete_the_sign_process_by_uploading_the_signed_pdf(self, browser, mocker):
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        with self.login(self.regular_user, browser=browser):
            browser.open(self.document.absolute_url() + '/@workflow/' + Document.draft_signing_transition,
                         method='POST',
                         headers=self.api_headers)

            self.assertEqual(0, self.document.get_current_version_id(missing_as_zero=True))

            token = urlsafe_b64encode(Signer(self.document).token_manager._get_token())
            url = self.document.absolute_url() + '/@upload-signed-pdf'

        # Upload the signed version as an anonym user with an access token
        browser.open(url,
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'access_token': token,
                                      'signed_pdf_data': b64encode('<DATA>')}))

        self.login(self.regular_user, browser)

        self.assertEqual(1, self.document.get_current_version_id(missing_as_zero=True))

        signed_version = Versioner(self.document).retrieve(1)
        self.assertEqual(u'<DATA>', signed_version.file.data)

    @browsing
    @requests_mock.Mocker()
    def test_complete_signing_invalidates_the_token(self, browser, mocker):
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        with self.login(self.regular_user, browser=browser):
            browser.open(self.document.absolute_url() + '/@workflow/' + Document.draft_signing_transition,
                         method='POST',
                         headers=self.api_headers)

            token = urlsafe_b64encode(Signer(self.document).token_manager._get_token())
            url = self.document.absolute_url() + '/@upload-signed-pdf'

            self.assertTrue(Signer(self.document).validate_token(token))

        browser.open(url,
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'access_token': token,
                                      'signed_pdf_data': b64encode('<DATA>')}))

        self.login(self.regular_user)
        with self.assertRaises(InvalidToken):
            Signer(self.document).validate_token(token)


class TestSignTransitions(SolrIntegrationTestCase):

    features = ['sign']

    @browsing
    @requests_mock.Mocker()
    def test_return_sign_redirect_url_when_signing_a_document_from_draft_state(self, browser, mocker):
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        self.login(self.regular_user, browser=browser)
        browser.open(self.document.absolute_url() + '/@workflow/' + Document.draft_signing_transition,
                     method='POST',
                     headers=self.api_headers)

        self.assertEqual('http://external.example.org/signing-requests/123',
                         browser.json.get('redirect_url'))

    @browsing
    @requests_mock.Mocker()
    def test_return_sign_redirect_url_when_signing_a_document_from_final_state(self, browser, mocker):
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        self.login(self.regular_user, browser=browser)

        browser.open(self.document.absolute_url() + '/@workflow/' + Document.finalize_transition,
                     method='POST',
                     headers=self.api_headers)

        browser.open(self.document.absolute_url() + '/@workflow/' + Document.final_signing_transition,
                     method='POST',
                     headers=self.api_headers)

        self.assertEqual('http://external.example.org/signing-requests/123',
                         browser.json.get('redirect_url'))
