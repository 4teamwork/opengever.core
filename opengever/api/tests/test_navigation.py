from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from urllib import urlencode


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

    @browsing
    def test_navigation_content_objects_can_be_overridden(self, browser):
        self.login(self.workspace_member, browser)
        params = [
            ('root_interface', 'opengever.workspace.interfaces.IWorkspace'),
            ('content_interfaces', 'opengever.workspace.interfaces.IWorkspaceFolder')
        ]

        browser.open(
            self.workspace.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        items = flatten_tree(browser.json.get('tree'))

        self.assertEqual(
            [self.workspace_folder.UID()],
            [item.get('uid') for item in items])

    @browsing
    def test_navigation_handles_multiple_content_interfaces(self, browser):
        self.login(self.workspace_member, browser)
        params = [
            ('root_interface', 'opengever.workspace.interfaces.IWorkspaceRoot'),
            ('content_interfaces', 'opengever.workspace.interfaces.IWorkspace'),
            ('content_interfaces', 'opengever.workspace.interfaces.IWorkspaceFolder')
        ]
        browser.open(
            self.workspace.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        items = flatten_tree(browser.json.get('tree'))

        self.assertEqual(
            [self.workspace.UID(), self.workspace_folder.UID()],
            [item.get('uid') for item in items])

    @browsing
    def test_lookup_propper_root_if_root_interface_is_within_content_interfaces(self, browser):
        self.login(self.workspace_member, browser)
        params = [
            ('root_interface', 'opengever.dossier.businesscase.IBusinessCaseDossier'),
            ('content_interfaces', 'opengever.dossier.businesscase.IBusinessCaseDossier')
        ]

        browser.open(
            self.subdossier.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        self.assertEqual(
            self.dossier.UID(),
            browser.json.get('tree')[0].get('uid'),
            "The root-object needs to be the last IBusinessCaseDossier")

    @browsing
    def test_raises_bad_request_when_not_existing_root_interface_provided(self, browser):
        self.login(self.workspace_member, browser)
        params = [
            ('root_interface', 'not.existing.Interface'),
        ]

        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
                headers={'Accept': 'application/json'},
            )

        self.assertEqual(
            {"message": "The provided `root_interface` could not be looked up: not.existing.Interface",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_raises_bad_request_when_not_existing_content_interfaces_provided(self, browser):
        self.login(self.workspace_member, browser)
        params = [
            ('content_interfaces', 'not.existing.Interface'),
        ]

        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
                headers={'Accept': 'application/json'},
            )

        self.assertEqual(
            {"message": "The provided `content_interfaces` could not be looked up: not.existing.Interface",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_allow_including_root_object(self, browser):
        self.login(self.workspace_member, browser)
        params = [
            ('root_interface', 'opengever.workspace.interfaces.IWorkspace'),
            ('content_interfaces', 'opengever.workspace.interfaces.IWorkspaceFolder'),
            ('include_root', True)
        ]

        browser.open(
            self.workspace.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        items = flatten_tree(browser.json.get('tree'))

        self.assertEqual(
            [self.workspace.UID(), self.workspace_folder.UID()],
            [item.get('uid') for item in items])

    @browsing
    def test_businesscasedossier_has_undefined_leaf_node(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('content_interfaces', 'opengever.dossier.businesscase.IBusinessCaseDossier')
        ]
        browser.open(
            self.portal.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIsNone(
            browser.json['tree'][0]['is_leafnode'],
            "Being a leaf node only makes sense for repository folders.",
        )

    @browsing
    def test_repositoryfolder_leaf_nodes(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.portal.absolute_url() + '/@navigation',
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        self.assertFalse(
            browser.json.get('tree')[0]['is_leafnode'],
            'The repo folder "http://nohost/plone/ordnungssystem/fuhrung" has children '
            'and thus must not be a leaf node.',
        )
        self.assertTrue(
            browser.json.get('tree')[0]['nodes'][0]['is_leafnode'],
             'The repo folder "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen" '
             'has no children and thus must be a leaf node.',
        )
