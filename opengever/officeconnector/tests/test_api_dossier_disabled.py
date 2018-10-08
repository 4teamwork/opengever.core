from ftw.testbrowser import browsing
from opengever.document.document import Document
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorDossierAPIDisabled(OCIntegrationTestCase):

    features = (
        '!officeconnector-attach',
        '!officeconnector-checkout',
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

    @browsing
    def test_create_with_oneoffixx(self, browser):
        self.login(self.dossier_responsible, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.shadow_document)
            self.assertIsNone(oc_url)
