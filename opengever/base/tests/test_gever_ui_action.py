from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.base.interfaces import IGeverSettings
from opengever.testing import IntegrationTestCase
from plone import api
import os


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
        self.assertEqual(['Properties'], editbar.menu_options("Actions"))

        self.activate_feature("gever_ui")
        browser.open(self.repository_root)
        self.assertEqual(['Properties', 'Switch to new UI'], editbar.menu_options("Actions"))

    @browsing
    def test_action_redirects_to_correct_url_for_repo(self, browser):
        self.activate_feature("gever_ui")
        self.login(self.regular_user, browser)
        obj = self.repository_root
        browser.open(obj)
        new_ui_base = api.portal.get_registry_record("opengever.base.interfaces.IGeverUI.path")
        url = browser.find("Switch to new UI").get("href")
        expected_url = os.path.join(new_ui_base, obj.virtual_url_path())
        self.assertEqual(expected_url, url)

    @browsing
    def test_action_redirects_to_correct_url_for_dossier(self, browser):
        self.activate_feature("gever_ui")
        self.login(self.regular_user, browser)
        obj = self.dossier
        browser.open(obj)
        new_ui_base = api.portal.get_registry_record("opengever.base.interfaces.IGeverUI.path")
        url = browser.find("Switch to new UI").get("href")
        expected_url = os.path.join(new_ui_base, obj.virtual_url_path())
        self.assertEqual(expected_url, url)

    @browsing
    def test_action_redirects_to_correct_url_for_document(self, browser):
        self.activate_feature("gever_ui")
        self.login(self.regular_user, browser)
        obj = self.document
        browser.open(obj)
        new_ui_base = api.portal.get_registry_record("opengever.base.interfaces.IGeverUI.path")
        url = browser.find("Switch to new UI").get("href")
        expected_url = os.path.join(new_ui_base, obj.virtual_url_path())
        self.assertEqual(expected_url, url)
