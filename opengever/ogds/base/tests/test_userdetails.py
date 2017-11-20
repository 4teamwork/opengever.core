from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestUserDetails(IntegrationTestCase):

    @browsing
    def test_user_details(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        self.assertEquals([u'B\xe4rfuss K\xe4thi (kathi.barfuss)'],
                          browser.css('h1.documentFirstHeading').text)

        metadata = dict(browser.css('.vertical').first.lists())
        self.assertDictContainsSubset({
            'Address': 'Kappelenweg 13 Postfach 1234 1234 Vorkappelen Schweiz',
            'Department': 'Staatskanzlei (SK)',
            'Description': 'nix',
            'Directorate': 'Staatsarchiv (Arch)',
            'Email': 'foo@example.com',
            'Email 2': 'bar@example.com',
            'Fax': '012 34 56 77',
            'Mobile phone': '012 34 56 76',
            'Name': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
            'Office phone': '012 34 56 78',
            'Salutation': 'Prof. Dr.',
            'Teams': u'Projekt \xdcberbaung Dorfmatte',
            'URL': 'http://www.example.com',
             }, metadata)

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
