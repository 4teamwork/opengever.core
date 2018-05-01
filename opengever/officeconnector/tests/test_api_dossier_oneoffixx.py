from ftw.testbrowser import browsing
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorDossierAPIWithOneOffixx(OCIntegrationTestCase):
    features = (
        'officeconnector-checkout',
        'oneoffixx'
    )

    @browsing
    def test_create_with_oneoffixx(self, browser):
        self.login(self.dossier_responsible, browser)
        self.document.file = None
        self.document.as_shadow_document()

        oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_oneoffixx_token(self.dossier_responsible, oc_url, (self.document,))
        payload = self.fetch_document_oneoffixx_payloads(browser, tokens)[0]

        self.validate_oneoffixx_payload(payload, self.document, self.dossier_responsible)

    @browsing
    def test_create_with_oneoffixx_when_not_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.document)

            self.assertIsNone(oc_url)
