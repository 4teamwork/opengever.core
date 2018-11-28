from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestFavoriteMenu(IntegrationTestCase):

    features = ('favorites', )

    @browsing
    def test_favorite_menu_is_shown(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        self.assertIsNotNone([], browser.css('#favorites-menu'))

        app_container = browser.css('#favorite-vue-app').first
        self.assertEqual('http://nohost/plone',
                         app_container.get('data-portalurl'))
        self.assertEqual('http://nohost/plone/favorites-view',
                         app_container.get('data-overviewurl'))
        self.assertEqual(self.regular_user.getId(),
                         app_container.get('data-userid'))

    @browsing
    def test_is_hiddend_when_favorite_feature_flag_is_disabled(self, browser):
        self.deactivate_feature('favorites')

        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        self.assertEqual([], browser.css('#favorites-menu'))
