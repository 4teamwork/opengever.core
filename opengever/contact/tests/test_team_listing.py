from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase


class TestTeamListing(IntegrationTestCase):

    @browsing
    def test_team_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder, view='tabbedview_view-teams')

        row = browser.css('.listing').first.dicts()[0]
        self.assertEquals(
            {'Active': 'Yes',
             'Org Unit': 'Finanzamt',
             'Group': 'Projekt A',
             'Title': u'Projekt \xdcberbaung Dorfmatte'},
            row)

        link = browser.css('.listing tr')[1].css('a').first
        self.assertEquals(
            u'Projekt \xdcberbaung Dorfmatte', link.text)
        self.assertEquals('http://nohost/plone/kontakte/team-1/view',
                          link.get('href'))

    @browsing
    def test_lists_only_active_teams_by_default(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.contactfolder, view='tabbedview_view-teams')
        expected_teams = [u'Projekt \xdcberbaung Dorfmatte', 'Sekretariat Abteilung Null', 'Sekretariat Abteilung XY']
        self.assertEqual(expected_teams, [team.get('Title') for team in browser.css('.listing').first.dicts()])

        Team.get('1').active = False
        create_session().flush()

        browser.open(self.contactfolder, view='tabbedview_view-teams')
        expected_teams = ['Sekretariat Abteilung Null', 'Sekretariat Abteilung XY']
        self.assertEquals(expected_teams, [team.get('Title') for team in browser.css('.listing').first.dicts()])

    @browsing
    def test_lists_also_inactive_teams_with_all_filter(self, browser):
        Team.get('1').active = False
        create_session().flush()

        self.login(self.regular_user, browser)
        browser.open(self.contactfolder, view='tabbedview_view-teams', data={'team_state_filter': 'filter_all'})
        expected_teams = [u'Projekt \xdcberbaung Dorfmatte', 'Sekretariat Abteilung Null', 'Sekretariat Abteilung XY']
        self.assertEqual(expected_teams, [team.get('Title') for team in browser.css('.listing').first.dicts()])

    @browsing
    def test_filtering_on_title(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.contactfolder, view='tabbedview_view-teams', data={'searchable_text': 'abteilung'})
        expected_teams = ['Sekretariat Abteilung Null', 'Sekretariat Abteilung XY']
        self.assertEqual(expected_teams, [team.get('Title') for team in browser.css('.listing').first.dicts()])
