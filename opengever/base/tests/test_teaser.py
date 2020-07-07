from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.ogds.models.user_settings import UserSettings


class TestTeaser(IntegrationTestCase):

    features = ('gever_ui',)

    @browsing
    def test_new_frontend_teaser_is_shown(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.portal)
        self.assertEqual(u'Do you already know the new user interface of OneGov GEVER? '
                         u'Try it out now. \xd7',
                         browser.css('#new-frontend-teaser').first.text)

    @browsing
    def test_new_frontend_teaser_is_not_shown_when_user_has_already_seen_it(self, browser):
        setting = UserSettings.query.filter_by(userid=self.regular_user.getId()).first()
        setting.seen_tours = ['be_new_frontend_teaser']
        self.login(self.regular_user, browser=browser)

        browser.visit(self.portal)
        self.assertEqual([], browser.css('#new-frontend-teaser'))

    @browsing
    def test_new_frontend_teaser_is_not_shown_if_gever_ui_is_disabled(self, browser):
        self.deactivate_feature('gever_ui')
        self.login(self.regular_user, browser=browser)
        browser.visit(self.portal)
        self.assertEqual([], browser.css('#new-frontend-teaser'))
