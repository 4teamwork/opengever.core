from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestRecentlyTouchedMenu(IntegrationTestCase):

    @browsing
    def test_recently_touched_menu_is_shown(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        self.assertIsNotNone([], browser.css('#recently-touched-menu'))

        app_container = browser.css('#recently-touched-vue-app').first
        self.assertEqual('http://nohost/plone',
                         app_container.get('data-portalurl'))
        self.assertEqual(self.regular_user.getId(),
                         app_container.get('data-userid'))
        self.assertEqual("0",
                         app_container.get('data-num-checked-out'))
