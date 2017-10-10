from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestUserDetails(IntegrationTestCase):

    @browsing
    def test_user_details(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        self.assertEquals([u'B\xe4rfuss K\xe4thi (kathi.barfuss)'],
                          browser.css('h1.documentFirstHeading').text)

        metadata = browser.css('.vertical').first.lists()

        self.assertEquals(
            ['Name', u'B\xe4rfuss K\xe4thi (kathi.barfuss)'], metadata[0])
        self.assertEquals(['Active', 'Yes'], metadata[1])
        self.assertEquals(['Email', 'kathi.barfuss@gever.local'], metadata[2])

    @browsing
    def test_user_details_return_not_found_for_not_exisiting_user(self, browser):
        with browser.expect_http_error(code=404):
            browser.login().open(self.portal, view='@@user-details/not.found')

    @browsing
    def test_list_all_team_memberships(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        self.assertEquals(
            [u'Projekt \xdcberbaung Dorfmatte'], browser.css('.teams li').text)
        self.assertEquals('http://nohost/plone/kontakte/team-1/view',
                          browser.css('.teams a').first.get('href'))
