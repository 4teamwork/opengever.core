from ftw.testbrowser import browsing
from opengever.document.document import Document
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorDossierAPIWithAttach(OCIntegrationTestCase):
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

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.regular_user,
            oc_url,
            (self.document, ),
            )

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
        self.inactive_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.regular_user,
            oc_url,
            (self.inactive_document, ),
            )

        payloads = self.fetch_document_attach_payloads(browser, tokens)

        self.assertEquals(200, browser.status_code)
        self.validate_attach_payload(payloads[0], self.inactive_document)

        file_contents = self.download_document(
            browser,
            tokens,
            payloads[0],
            )

        self.assertEquals(file_contents, self.inactive_document.file.data)

    @browsing
    def test_attach_to_email_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.archive_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.archive_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        oc_url = self.fetch_document_attach_oc_url(browser, self.archive_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.regular_user,
            oc_url,
            (self.archive_document, ),
            )

        payloads = self.fetch_document_attach_payloads(browser, tokens)

        self.assertEquals(200, browser.status_code)
        self.validate_attach_payload(payloads[0], self.archive_document)

        file_contents = self.download_document(
            browser,
            tokens,
            payloads[0],
            )

        self.assertEquals(file_contents, self.archive_document.file.data)

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

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.regular_user,
            oc_url,
            documents,
            )

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

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.regular_user,
            oc_url,
            documents,
            )

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

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.regular_user,
            oc_url,
            documents,
            )

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
        self.archive_document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.archive_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.archive_document,
                )

            self.assertIsNone(oc_url)
