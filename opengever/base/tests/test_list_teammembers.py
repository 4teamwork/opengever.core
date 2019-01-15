from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestTeamMembersView(IntegrationTestCase):

    @browsing
    def test_list_teammembers_view(self, browser):
        self.login(self.regular_user, browser)
        browser.open(view='list_teammembers', data={'team': 1})
        self.assertSequenceEqual(
            [u'B\xe4rfuss K\xe4thi (kathi.barfuss)', u'Ziegler Robert (robert.ziegler)'],
            browser.css('.member_listing li a').text,
        )

    @browsing
    def test_list_teammembers_view_with_nonexisting_group(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(view='list_teammembers', data={'team': 0})
            self.assertEqual(['no group id'], browser.css('p').text)

    @browsing
    def test_list_teammembers_view_with_empty_group(self, browser):
        self.login(self.regular_user, browser)
        browser.open(view='list_teammembers', data={'team': 3})
        self.assertEqual(['There are no members in this group.'], browser.css('p').text)
