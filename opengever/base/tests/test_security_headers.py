from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from Products.Five.browser import BrowserView
from zope.component import getSiteManager
from zope.interface import Interface


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

    @browsing
    def test_browser_view_can_override_csp(self, browser):

        class CSPTestView(BrowserView):
            def __call__(self):
                self.request.response.setHeader(
                    'Content-Security-Policy', 'default-src *')

        getSiteManager().registerAdapter(
            CSPTestView, (Interface, Interface), Interface, name=u'csp-test')

        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='csp-test')
        self.assertEqual(browser.headers['Content-Security-Policy'], 'default-src *')
