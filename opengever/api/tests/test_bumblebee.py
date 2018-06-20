from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestBumblebeeSession(IntegrationTestCase):

    @browsing
    def test_create_bumblebee_session(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal.absolute_url() + '/@preview-session',
            method='POST',
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 204)
        self.assertIn('bumblebee-local', browser.cookies)
