from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase


class TestTeamAddForm(IntegrationTestCase):

    @browsing
    def test_add_new_team_form_is_only_available_for_administrators_and_managers(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(self.contactfolder, view='add-team')

        self.login(self.administrator, browser)
        browser.open(self.contactfolder, view='add-team')

        self.login(self.manager, browser)
        browser.open(self.contactfolder, view='add-team')

    @browsing
    def test_add_new_team(self, browser):
        self.login(self.administrator, browser)
        browser.raise_http_errors = False
        browser.open(self.contactfolder, view='add-team')
        browser.fill({'Title': u'Projekt \xdcberbaung Dorfmatte'})
        form = browser.find_form_by_field('Group')
        form.find_widget('Org Unit').fill('fa')
        form.find_widget('Group').fill('projekt_a')
        browser.find('Save').click()
        self.assertEquals(4, len(Team.query.all()))

        team = Team.query.get(4)
        self.assertEquals('projekt_a', team.groupid)
        self.assertEquals(u'Projekt \xdcberbaung Dorfmatte', team.title)
        self.assertEquals('fa', team.org_unit_id)


class TestTeamEditForm(IntegrationTestCase):

    @browsing
    def test_editing_a_team(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.contactfolder, view='team-1/edit')
        browser.fill({'Title': u'Projekt \xdcberbaung Dorf S\xfcd'})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(u'Projekt \xdcberbaung Dorf S\xfcd', Team.get('1').title)

    @browsing
    def test_values_injected_correclty(self, browser):
        self.login(self.administrator, browser=browser)
        team = Team.get(1)
        team.active = False
        browser.open(self.contactfolder, view='team-1/edit')

        form = browser.forms['form']
        self.assertEquals(u'Projekt \xdcberbaung Dorfmatte', form.find_field('Title').value)
        self.assertIsNone(form.find_field('Active').get('checked'))
        self.assertEquals(u'projekt_a', form.find_field('Group').value)
        self.assertEquals(u'fa', form.find_field('Org Unit').value)

    @browsing
    def test_editing_is_only_available_for_administrators_and_managers(self, browser):
        with browser.expect_unauthorized():
            self.login(self.regular_user, browser=browser)
            browser.open(self.contactfolder, view='team-1/edit')

        self.login(self.administrator, browser=browser)
        browser.open(self.contactfolder, view='team-1/edit')

        self.login(self.manager, browser=browser)
        browser.open(self.contactfolder, view='team-1/edit')


class TestTeamEditAction(IntegrationTestCase):

    @browsing
    def test_edit_link_is_visible_for_administrators(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.contactfolder, view='team-1/view')
        self.assertEquals(['Edit'], browser.css('#content-views').text)

        url = browser.css('#content-views a')[0].get('href')
        self.assertTrue(url.startswith('http://nohost/plone/kontakte/team-1/edit'))

    @browsing
    def test_edit_link_is_visible_for_managers(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.contactfolder, view='team-1/view')
        self.assertEquals(['Edit'], browser.css('#content-views').text)

        url = browser.css('#content-views a')[0].get('href')
        self.assertTrue(url.startswith('http://nohost/plone/kontakte/team-1/edit'))

    @browsing
    def test_edit_link_is_not_visible_for_regular_users(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder, view='team-1/view')
        self.assertEquals([''], browser.css('#content-views').text)
