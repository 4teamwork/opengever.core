from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


def flatten_tree(items):
    flattened_items = []

    def flatten(items):
        for item in items:
            flattened_items.append(item)
            flatten(item.get('nodes', []))

    flatten(items)
    return flattened_items


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

    @browsing
    def test_current_context_item_is_marked(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.leaf_repofolder.absolute_url() + '/@navigation',
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        current_items = filter(
            lambda item: item.get('current'),
            flatten_tree(browser.json.get('tree')))

        self.assertEqual(1, len(current_items))

        current_item = current_items[0]
        self.assertEqual(current_item.get('uid'), self.leaf_repofolder.UID())

    @browsing
    def test_current_tree_items_are_marked(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier.absolute_url() + '/@navigation',
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        current_items = filter(
            lambda item: item.get('current_tree'),
            flatten_tree(browser.json.get('tree')))

        self.assertEqual(
            [self.branch_repofolder.UID(), self.leaf_repofolder.UID()],
            [item.get('uid') for item in current_items])

