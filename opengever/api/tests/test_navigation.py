from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestNavigation(IntegrationTestCase):

    @browsing
    def test_navigation_contains_respository(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal.absolute_url() + '/@navigation',
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'tree', browser.json)
        self.assertEqual(
            browser.json['@id'],
            u'http://nohost/plone/ordnungssystem/@navigation')

    @browsing
    def test_navigation_on_subcontext(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document.absolute_url() + '/@navigation',
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'tree', browser.json)
        self.assertEqual(
            browser.json['@id'],
            u'http://nohost/plone/ordnungssystem/@navigation')

    @browsing
    def test_navigation_id_in_components(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document.absolute_url(),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json['@components']['navigation']['@id'],
            u'http://nohost/plone/ordnungssystem/@navigation')
