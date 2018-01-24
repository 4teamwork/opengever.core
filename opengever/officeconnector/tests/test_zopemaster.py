from ftw.testbrowser import browsing
from hashlib import sha256
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorAsZopemasterDossierAPIWithAttach(OCIntegrationTestCase):
    features = (
        'officeconnector-attach',
    )

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.manager, browser)

        oc_url = self.fetch_document_attach_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.manager,
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


class TestOfficeconnectorAsZopemasterDossierAPIWithCheckout(OCIntegrationTestCase):
    features = (
        'officeconnector-checkout',
    )

    @browsing
    def test_checkout_checkin_open_with_file_without_comment(self, browser):
        self.login(self.manager, browser)

        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_checkout_token(self.manager, oc_url)
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
