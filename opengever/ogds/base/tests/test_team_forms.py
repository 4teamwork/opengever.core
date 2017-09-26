from ftw.testbrowser import browsing
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase


class TestTeamAddForm(IntegrationTestCase):

    @browsing
    def test_add_new_team_form_is_only_available_for_manager(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(self.contactfolder, view='add-team')

        self.login(self.manager, browser)
        browser.open(self.contactfolder, view='add-team')

    @browsing
    def test_add_new_team(self, browser):
        self.login(self.manager, browser)

        browser.raise_http_errors = False

        browser.open(self.contactfolder, view='add-team')
        browser.fill({'Title': u'Projekt \xdcberbaung Dorfmatte'})

        form = browser.find_form_by_field('Group')
        form.find_widget('Org Unit').fill('fa')
        form.find_widget('Group').fill('projekt_a')
        browser.find('Save').click()

        self.assertEquals(3, len(Team.query.all()))
        team = Team.query.get(3)
        self.assertEquals('projekt_a', team.groupid)
        self.assertEquals(u'Projekt \xdcberbaung Dorfmatte', team.title)
        self.assertEquals('fa', team.org_unit_id)
