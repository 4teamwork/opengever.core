from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.sign.sign import Signer
from opengever.testing.integration_test_case import IntegrationTestCase
from os import environ
import requests_mock
from zExceptions import BadRequest


@requests_mock.Mocker()
class TestSignDocumentPost(IntegrationTestCase):

    @browsing
    def test_successfully_starts_signing_process(self, mocker, browser):
        self.login(self.regular_user, browser)

        freezed_now = datetime(2001, 1, 1)
        mocker.post(environ.get('SIGN_SERVICE_URL'), json=[])

        with freeze(freezed_now):
            browser.open(self.document, view='@sign',
                         method='POST', headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)

        sign_requests = Signer(self.document).storage.items()
        self.assertEqual(1, len(sign_requests))
        self.assertEqual(
            [{"userid": self.regular_user.id, 'created':freezed_now, 'state': 'pending'}],
            sign_requests[0][0])

    @browsing
    def test_fails_if_document_is_not_finalizable(self, mocker, browser):
        self.login(self.regular_user, browser)

        self.checkout_document(self.document)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.document, view='@sign',
                         method='POST', headers=self.api_headers)

        self.assertEqual('Document not finalizable', cm.message)
