from ftw.testbrowser import browsing
from hashlib import sha256
from opengever.document.document import Document
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorAPIDisabled(OCIntegrationTestCase):
    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

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
        self.set_workflow_state('dossier-state-inactive', self.dossier)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

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
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)
        self.document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)


class TestOfficeconnectorAPIWithAttach(OCIntegrationTestCase):
    features = (
        'officeconnector-attach',
    )

    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        oc_url = self.fetch_document_attach_oc_url(browser, self.document)

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(oc_url, (self.document, ))
        payloads = self.fetch_document_attach_payloads(browser, tokens)

        self.assertEquals(200, browser.status_code)
        self.validate_attach_payload(payloads[0], self.document)

        file_contents = self.download_document(
            browser,
            tokens,
            payloads[0],
            )

        self.assertEquals(file_contents, self.document.file.data)

    @browsing
    def test_attach_to_email_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        oc_url = self.fetch_document_attach_oc_url(browser, self.document)

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(oc_url, (self.document, ))
        payloads = self.fetch_document_attach_payloads(browser, tokens)

        self.assertEquals(200, browser.status_code)
        self.validate_attach_payload(payloads[0], self.document)

        file_contents = self.download_document(
            browser,
            tokens,
            payloads[0],
            )

        self.assertEquals(file_contents, self.document.file.data)

    @browsing
    def test_attach_to_email_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        oc_url = self.fetch_document_attach_oc_url(browser, self.document)

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(oc_url, (self.document, ))
        payloads = self.fetch_document_attach_payloads(browser, tokens)

        self.assertEquals(200, browser.status_code)
        self.validate_attach_payload(payloads[0], self.document)

        file_contents = self.download_document(
            browser,
            tokens,
            payloads[0],
            )

        self.assertEquals(file_contents, self.document.file.data)

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

        oc_url = self.fetch_dossier_multiattach_oc_url(
            browser,
            self.dossier,
            documents,
            dossier_email,
            )

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(oc_url, documents)
        payloads = self.fetch_document_attach_payloads(browser, tokens)

        for payload in zip(payloads, documents):
            self.validate_attach_payload(payload[0], payload[1])

    @browsing
    def test_attach_many_to_email_inactive(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertFalse(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(
            browser,
            self.dossier,
            documents,
            dossier_email,
            )

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(oc_url, documents)
        payloads = self.fetch_document_attach_payloads(browser, tokens)

        for payload in zip(payloads, documents):
            self.validate_attach_payload(payload[0], payload[1])

    @browsing
    def test_attach_many_to_email_resolved(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertFalse(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(
            browser,
            self.dossier,
            documents,
            dossier_email,
            )

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(oc_url, documents)
        payloads = self.fetch_document_attach_payloads(browser, tokens)

        for payload in zip(payloads, documents):
            self.validate_attach_payload(payload[0], payload[1])

    @browsing
    def test_checkout_checkin_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)
        self.document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)


class TestOfficeconnectorAPIWithCheckout(OCIntegrationTestCase):
    features = (
        'officeconnector-checkout',
    )
    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

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
        self.set_workflow_state('dossier-state-inactive', self.dossier)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

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
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_with_file_without_comment(self, browser):
        self.login(self.regular_user, browser)

        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_checkout_token(oc_url)
        payload = self.fetch_document_checkout_payloads(browser, tokens)[0]

        self.validate_checkout_payload(payload, self.document)

        self.checkout_document(browser, tokens, payload, self.document)

        lock_token = self.lock_document(browser, tokens, self.document)

        original_checksum = sha256(
            self.download_document(browser, tokens, payload),
            ).hexdigest()

        with open('../../opengever/testing/assets/addendum.docx') as f:
            self.upload_document(browser, tokens, payload, self.document, f)

        new_checksum = sha256(
            self.download_document(browser, tokens, payload),
            ).hexdigest()

        self.assertNotEquals(new_checksum, original_checksum)

        self.unlock_document(browser, tokens, self.document, lock_token)

        self.checkin_document(browser, tokens, payload, self.document)

    @browsing
    def test_checkout_checkin_open_with_file_with_comment(self, browser):
        self.login(self.regular_user, browser)

        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_checkout_token(oc_url)
        payload = self.fetch_document_checkout_payloads(browser, tokens)[0]

        self.validate_checkout_payload(payload, self.document)

        self.checkout_document(browser, tokens, payload, self.document)

        lock_token = self.lock_document(browser, tokens, self.document)

        original_checksum = sha256(
            self.download_document(browser, tokens, payload),
            ).hexdigest()

        with open('../../opengever/testing/assets/addendum.docx') as f:
            self.upload_document(browser, tokens, payload, self.document, f)

        new_checksum = sha256(
            self.download_document(browser, tokens, payload),
            ).hexdigest()

        self.assertNotEquals(new_checksum, original_checksum)

        self.unlock_document(browser, tokens, self.document, lock_token)

        self.checkin_document(
            browser,
            tokens,
            payload,
            self.document,
            comment='foobar',
            )

    @browsing
    def test_checkout_checkin_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)
        self.document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)
