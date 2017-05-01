from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestAnonymousAccess(FunctionalTestCase):

    @browsing
    def test_anonymous_cannot_access_search(self, browser):
        with browser.expect_unauthorized():
            browser.visit(self.portal, view='search')

    @browsing
    def test_anonymous_can_access_login_form(self, browser):
        browser.visit(self.portal, view='login_form')
        self.assertEquals(self.portal.absolute_url() + '/login_form',
                          browser.url)

    @browsing
    def test_authenticated_can_access_search(self, browser):
        browser.login().visit(self.portal, view='search')
        self.assertEquals(self.portal.absolute_url() + '/@@search',
                          browser.url)
