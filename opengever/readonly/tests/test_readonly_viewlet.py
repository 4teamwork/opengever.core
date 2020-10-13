from ftw.testbrowser import browsing
from opengever.readonly import is_in_readonly_mode
from opengever.testing import FunctionalTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode


class TestReadOnlyViewlet(FunctionalTestCase):

    @browsing
    def test_readonly_message_not_visible_when_disabled(self, browser):
        browser.login()
        browser.open(self.portal)

        self.assertEqual(0, len(browser.css('#readonly-message')))

    @browsing
    def test_readonly_message_visible_when_enabled(self, browser):
        browser.login()

        with ZODBStorageInReadonlyMode():
            browser.open(self.portal)

            viewlet = browser.css('#readonly-message').first
            self.assertIsNotNone(viewlet)
            self.assertIn(
                u'GEVER is currently in readonly mode',
                viewlet.normalized_text())

            self.assertTrue(self.portal._p_jar.isReadOnly())
            self.assertTrue(is_in_readonly_mode())
