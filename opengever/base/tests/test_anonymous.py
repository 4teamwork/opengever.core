from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestAnonymousAccess(IntegrationTestCase):

    @browsing
    def test_anonymous_cannot_access_search(self, browser):
        with browser.expect_unauthorized():
            browser.open(self.portal, view='search')

    @browsing
    def test_anonymous_can_access_login_form(self, browser):
        browser.open(self.portal, view='login_form')
        self.assertEquals(self.portal.absolute_url() + '/login_form',
                          browser.url)

    @browsing
    def test_authenticated_can_access_search(self, browser):
        self.login(self.regular_user, browser=browser)

        # needed because of the TranslatedTitle brain patch
        browser.open()
        browser.click_on("Deutsch")

        browser.open(self.portal, view='@@search')

        self.assertEquals(self.portal.absolute_url() + '/@@search',
                          browser.url)
