from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestPersonalPreferencesForm(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_shows_notification_form(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='personal-preferences')

        div = browser.css('#notification-settings-form').first
        self.assertEquals('http://nohost/plone/notification-settings/list',
                          div.get('data-list-url'))
        self.assertEquals('http://nohost/plone/notification-settings/save_notification_setting',
                          div.get('data-save-url'))
        self.assertEquals('http://nohost/plone/notification-settings/reset_notification_setting',
                          div.get('data-reset-url'))
