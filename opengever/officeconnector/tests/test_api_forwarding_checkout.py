from ftw.testbrowser import browsing
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorForwardingAPIWithCheckout(OCIntegrationTestCase):

    features = (
        '!officeconnector-attach',
        'officeconnector-checkout',
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

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(
                browser,
                self.inbox_forwarding_document,
                )

            self.assertIsNone(oc_url)
