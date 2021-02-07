from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD


class TestSessionCookie(IntegrationTestCase):
    """Test session cookie flags
    """

    @browsing
    def test_session_cookie_flags(self, browser):
        browser.open(self.portal, view='login_form')
        browser.fill(
            {'Login Name': TEST_USER_NAME, 'Password': TEST_USER_PASSWORD})
        browser.click_on('Log in')

        session_cookie = browser.get_driver().response.cookies['__ac']
        self.assertEqual(session_cookie.get('same_site'), 'Lax')
        self.assertTrue(session_cookie.get('secure'))
        self.assertTrue(session_cookie.get('http_only'))
