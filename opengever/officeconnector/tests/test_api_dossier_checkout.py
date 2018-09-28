from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from hashlib import sha256
from opengever.document.document import Document
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
from opengever.testing.assets import path_to_asset
import jwt


class TestOfficeconnectorDossierAPIWithCheckout(OCIntegrationTestCase):

    features = (
        '!officeconnector-attach',
        'officeconnector-checkout',
    )

    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.expired_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.expired_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_many_to_email_open(self, browser):
        self.login(self.regular_user, browser)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        with browser.expect_http_error(404):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_many_to_email_inactive(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertIsNone(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        with browser.expect_http_error(404):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_many_to_email_resolved(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertIsNone(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        with browser.expect_http_error(404):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_with_file_without_comment(self, browser):
        self.login(self.regular_user, browser)

        with freeze(datetime(2100, 8, 3, 15, 25)):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(token, expected_token)

        expected_payloads = [{
            u'checkin-with-comment': u'@@checkin_document',
            u'checkin-without-comment': u'checkin_without_comment',
            u'checkout': u'@@checkout_documents',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'upload-api': None,
            u'upload-form': u'file_upload',
            u'uuid': u'createtreatydossiers000000000002',
            }]
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.get('csrf-token'))
            self.assertDictContainsSubset(expected_payload, payload)

        self.checkout_document(browser, raw_token, payloads[0], self.document)

        lock_token = self.lock_document(browser, raw_token, self.document)

        original_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document(browser, raw_token, payloads[0], self.document, f)

        new_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        self.assertNotEquals(new_checksum, original_checksum)

        self.unlock_document(browser, raw_token, self.document, lock_token)
        self.checkin_document(browser, raw_token, payloads[0], self.document)

    @browsing
    def test_checkout_checkin_open_with_file_with_comment(self, browser):
        self.login(self.regular_user, browser)

        with freeze(datetime(2100, 8, 3, 15, 25)):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(token, expected_token)

        expected_payloads = [{
            u'checkin-with-comment': u'@@checkin_document',
            u'checkin-without-comment': u'checkin_without_comment',
            u'checkout': u'@@checkout_documents',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'upload-api': None,
            u'upload-form': u'file_upload',
            u'uuid': u'createtreatydossiers000000000002',
            }]
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.get('csrf-token'))
            self.assertDictContainsSubset(expected_payload, payload)

        self.checkout_document(browser, raw_token, payloads[0], self.document)

        lock_token = self.lock_document(browser, raw_token, self.document)

        original_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document(browser, raw_token, payloads[0], self.document, f)

        new_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        self.assertNotEqual(new_checksum, original_checksum)

        self.unlock_document(browser, raw_token, self.document, lock_token)
        self.checkin_document(
            browser,
            raw_token,
            payloads[0],
            self.document,
            comment='foobar',
            )

    @browsing
    def test_checkout_checkin_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.inactive_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.inactive_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.expired_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.expired_document,
                )

            self.assertIsNone(oc_url)
