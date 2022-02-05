from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestSecurityHeaders(IntegrationTestCase):

    @browsing
    def test_response_contains_security_related_headers(self, browser):
        browser.open(self.portal, view='login_form')
        self.assertEqual(browser.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(browser.headers['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(
            browser.headers['Content-Security-Policy'],
            "default-src 'self' 'unsafe-eval' 'unsafe-inline'; "
            "img-src 'self' data:; object-src 'none'; frame-ancestors 'none'")
        self.assertEqual(browser.headers['Referrer-Policy'], 'same-origin')
