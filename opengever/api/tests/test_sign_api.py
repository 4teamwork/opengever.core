from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
import json
from opengever.sign.sign import Signer
from opengever.testing.integration_test_case import IntegrationTestCase
from os import environ
import requests_mock
from zExceptions import BadRequest
from zExceptions.unauthorized import Unauthorized


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
            {"userid": self.regular_user.id, 'created':freezed_now, 'state': 'pending'},
            sign_requests[0][1])

    @browsing
    def test_fails_if_document_is_not_finalizable(self, mocker, browser):
        self.login(self.regular_user, browser)

        self.checkout_document(self.document)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.document, view='@sign',
                         method='POST', headers=self.api_headers)

        self.assertEqual('Document not finalizable', str(cm.exception))


class TestSignSatusPatch(IntegrationTestCase):

    @browsing
    def test_raises_with_no_token(self, browser):
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized) as cm:
            browser.open(self.document, view='@update-sign-state',
                         method='PATCH', headers=self.api_headers)

    @browsing
    def test_raises_with_invalid_token(self, browser):
        browser.exception_bubbling = True

        data = {'token': 'invalid', 'state': 'failed'}

        with self.assertRaises(Unauthorized) as cm:
            browser.open(self.document, view='@update-sign-state',
                         data=json.dumps(data),
                         method='PATCH', headers=self.api_headers)

    @browsing
    def test_successfull_state_upate(self, browser):
        browser.exception_bubbling = True

        self.login(self.regular_user)

        token = Signer(self.document).register_signing()
        data = {'token': token, 'state': 'failed'}

        browser.open(self.document, view='@update-sign-state',
                     data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(
            'failed',
            Signer(self.document).storage.get(token).get('state'))


class TestSignPost(IntegrationTestCase):
    pass
