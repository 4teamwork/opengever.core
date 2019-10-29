from ftw.testbrowser import browsing
from opengever.base.interfaces import IGeverSettings
from opengever.testing import IntegrationTestCase


class TestGeverUIAction(IntegrationTestCase):

    def test_feature_disabled_by_default(self):
        self.login(self.regular_user)
        settings = IGeverSettings(self.portal).get_features()
        self.assertIn("gever_ui_enabled", settings)
        self.assertFalse(settings.get("gever_ui_enabled"))

    @browsing
    def test_action_is_visible_when_feature_enabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.repository_root)

        self.assertEqual(
            [],
            browser.css('#portal-personaltools #personaltools-switch_ui').text)

        self.activate_feature("gever_ui")
        browser.open(self.repository_root)

        self.assertEqual(
            ['Switch UI'],
            browser.css('#portal-personaltools #personaltools-switch_ui').text)
