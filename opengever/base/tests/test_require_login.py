from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
import transaction
import urllib


class TestRequireLoginScript(IntegrationTestCase):

    @browsing
    def test_require_login_redirects_to_came_from_if_already_logged_in(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='require_login?came_from={}'.format(
            urllib.quote(self.document.absolute_url())))

        self.assertEqual(self.document.absolute_url(), browser.url.split('?')[0])

    @browsing
    def test_require_login_displays_login_form_and_redirecs_upon_login(self, browser):
        self.login(self.regular_user, browser=browser)
        document_url = self.document.absolute_url()
        self.logout(browser=browser)

        # Disable the `cookie only over https flag, activated
        # by `opengever.core.hooks.installed`.
        self.portal.acl_users.session.secure = False

        with browser.expect_unauthorized():
            browser.open(
                view='require_login?came_from={}'.format(
                    urllib.quote(document_url)))

        self.assertTrue(
            browser.url.startswith('http://nohost/plone/require_login'),
            'Unexpected URL {}'.format(browser.url))

        browser.fill({'Login Name': self.regular_user.id,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertEqual(document_url, browser.url)

    @browsing
    def test_unauthorized_visible_when_raised_in_traversal(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_unauthorized():
            browser.open(view='test-traversal-unauthorized')

    @browsing
    def test_unauthorized_visible_when_raised_in_publishing(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_unauthorized():
            browser.open(view='test-publishing-unauthorized')
        self.assertEquals('Insufficient Privileges', plone.first_heading())

    @browsing
    def test_unauthorized_when_came_from_does_not_exist(self, browser):
        # When the came_from URL does not exist, we want the regular unauthorized
        # page to appear when logged in.
        url = ('{0}/acl_users/credentials_cookie_auth/require_login'
               '?came_from={0}/does/not/exist').format(self.portal.absolute_url())

        self.login(self.regular_user, browser=browser)
        with browser.expect_unauthorized():
            browser.open(url)

        self.assertEquals('Insufficient Privileges', plone.first_heading())
