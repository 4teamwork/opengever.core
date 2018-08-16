from ftw.testbrowser import browsing
from opengever.base.interfaces import IGeverSettings
from opengever.testing import IntegrationTestCase


class TestGetSettingView(IntegrationTestCase):

    @browsing
    def test_get_setting_view_returns_feature_values(self, browser):
        self.login(self.regular_user)
        features = IGeverSettings(self.portal).get_features()
        self.assertTrue(len(features) > 0)
        for feature, value in features.items():
            self.assertEqual(value,
                             self.portal.unrestrictedTraverse("get_setting/{}".format(feature)))

    @browsing
    def test_get_setting_view_returns_setting_values(self, browser):
        self.login(self.regular_user)
        settings = IGeverSettings(self.portal).get_settings()
        self.assertTrue(len(settings) > 0)
        for setting, value in settings.items():
            self.assertEqual(value,
                             self.portal.unrestrictedTraverse("get_setting/{}".format(setting)))

    def test_get_setting_view_raises_key_Error(self):
        self.login(self.regular_user)
        with self.assertRaises(KeyError):
            self.portal.unrestrictedTraverse("get_setting/foo")
