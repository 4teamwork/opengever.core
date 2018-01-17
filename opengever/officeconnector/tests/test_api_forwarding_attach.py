from ftw.testbrowser import browsing
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorForwardingAPIWithAttach(OCIntegrationTestCase):
    features = (
        'officeconnector-attach',
    )

    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.secretariat_user, browser)
        self.inbox_forwarding_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(
                browser,
                self.inbox_forwarding_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.secretariat_user, browser)

        oc_url = self.fetch_document_attach_oc_url(
            browser,
            self.inbox_forwarding_document,
            )

        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        tokens = self.validate_attach_token(
            self.secretariat_user,
            oc_url,
            (self.inbox_forwarding_document, ),
            )

        payloads = self.fetch_document_attach_payloads(browser, tokens)

        self.assertEquals(200, browser.status_code)
        self.validate_attach_payload(
            payloads[0],
            self.inbox_forwarding_document,
            )

        file_contents = self.download_document(
            browser,
            tokens,
            payloads[0],
            )

        self.assertEquals(
            file_contents,
            self.inbox_forwarding_document.file.data,
            )
