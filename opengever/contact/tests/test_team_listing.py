from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase


class TestTeamListing(IntegrationTestCase):

    @browsing
    def test_team_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder, view='tabbedview_view-teams')
        expected_listing = [
            {
                'Active': 'Yes',
                'Group': 'Projekt A',
                'Org Unit': u'Finanz\xe4mt',
                'Title': u'Projekt \xdcberbaung Dorfmatte',
            },
            {
                'Active': 'Yes',
                'Group': u'Projekt L\xc3\xa4\xc3\xa4r',
                'Org Unit': u'Finanz\xe4mt',
                'Title': 'Sekretariat Abteilung Null',
            },
            {
                'Active': 'Yes',
                'Group': 'Projekt B',
                'Org Unit': u'Finanz\xe4mt',
                'Title': 'Sekretariat Abteilung XY',
            },
        ]
        self.assertEqual(expected_listing, browser.css('.listing').first.dicts())

        expected_links = [
            (u'Projekt \xdcberbaung Dorfmatte', 'http://nohost/plone/kontakte/team-1/view'),
            ('Sekretariat Abteilung Null', 'http://nohost/plone/kontakte/team-3/view'),
            ('Sekretariat Abteilung XY', 'http://nohost/plone/kontakte/team-2/view'),
        ]
        self.assertEqual(
            expected_links,
            [(row.text, row.get('href')) for row in browser.css('.listing a')],
        )

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
