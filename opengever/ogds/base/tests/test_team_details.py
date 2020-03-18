from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing


class TestTeamDetails(IntegrationTestCase):

    @browsing
    def test_title(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.contactfolder, view='team-1/view')

        self.assertEquals(
            [u'Projekt \xdcberbaung Dorfmatte'], browser.css('h1').text)

    @browsing
    def test_raises_not_found_with_invalid_id(self, browser):
        self.login(self.administrator, browser=browser)

        with browser.expect_http_error(code=404):
            browser.open(self.contactfolder, view='team-123/view')

    @browsing
    def test_metadata_table(self, browser):
        self.login(self.administrator, browser=browser)
        browser.raise_http_errors = False
        browser.open(self.contactfolder, view='team-1/view')

        items = browser.css('.listing').first.lists()
        self.assertEqual(
            ['Assigned org unit', u'Finanz\xe4mt'], items[0])
        self.assertEqual(
            ['Group', 'Projekt A'], items[1])

    @browsing
    def test_metadata_table_shows_groupid_if_group_has_no_title(self, browser):
        self.login(self.administrator, browser=browser)
        browser.raise_http_errors = False

        team = Team.get(1)
        group = Team.get(1).group
        group.title = ""

        browser.open(self.contactfolder, view='team-1/view')
        items = browser.css('.listing').first.lists()
        self.assertEquals(
            ['Assigned org unit', team.org_unit.title], items[0])
        self.assertEquals(
            ['Group', group.groupid], items[1])

    @browsing
    def test_list_and_link_team_members(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.contactfolder, view='team-1/view')

        links = browser.css('.members a')
        self.assertEquals(
            [u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             'Ziegler Robert (robert.ziegler)'],
            links.text)

        self.assertEquals(
            ['http://nohost/plone/kontakte/user-kathi.barfuss/view',
             'http://nohost/plone/kontakte/user-robert.ziegler/view'],
            [link.get('href') for link in links])

    @browsing
    def test_byline_is_not_shown(self, browser):
        self.login(self.administrator, browser=browser)

        byline_css_selector = '.documentByLine'

        # test-precondition: byline is shown for the contactfolder
        browser.open(self.contactfolder)
        self.assertIsNotNone(browser.css(byline_css_selector))

        browser.open(self.contactfolder, view='team-1/view')
        self.assertEquals([], browser.css(byline_css_selector))
