from ftw.testbrowser import browsing
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import obj2brain
from opengever.testing import SolrIntegrationTestCase
from opengever.testing.helpers import MockDossierTypes
from opengever.trash.trash import ITrasher
from plone import api
from urllib import urlencode
import Missing


def flatten_tree(items):
    flattened_items = []

    def flatten(items):
        for item in items:
            flattened_items.append(item)
            flatten(item.get('nodes', []))

    flatten(items)
    return flattened_items


class TestNavigation(SolrIntegrationTestCase):

    @browsing
    def test_navigation_contains_respository(self, browser):
        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@navigation'
        browser.open(
            url,
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'tree', browser.json)
        self.assertEqual(
            browser.json['@id'],
            u'http://nohost/plone/@navigation')

    @browsing
    def test_navigation_on_subcontext(self, browser):
        self.login(self.regular_user, browser)
        url = self.document.absolute_url() + '/@navigation'
        browser.open(
            url,
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'tree', browser.json)
        self.assertEqual(
            browser.json['@id'],
            url)

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
            self.document.absolute_url() + '/@navigation')

    @browsing
    def test_navigation_id_is_present_in_components_even_if_no_root_is_found(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('root_interface', 'opengever.base.interfaces.IGeverUI'),
        ]

        # when not expanding, @id of navigation should always be in the response
        browser.open(
            self.document.absolute_url() + '?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )

        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json['@components']['navigation']['@id'],
            self.document.absolute_url() + '/@navigation')

        # when expanding, not finding the root will raise a BadRequest
        params.append(('expand', 'navigation'))
        with browser.expect_http_error(400):
            browser.open(
                self.document.absolute_url() + '?{}'.format(urlencode(params)),
                headers={'Accept': 'application/json'},
            )
        self.assertEqual(
            {"message": "No root found for interface: opengever.base.interfaces.IGeverUI",
             "type": "BadRequest"},
            browser.json)

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
    def test_lookup_proper_root_if_root_interface_is_within_content_interfaces(self, browser):
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
    def test_lookup_proper_root_if_root_is_not_within_acquisition_chain_of_context(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('root_interface', 'opengever.repository.repositoryroot.IRepositoryRoot'),
            ('content_interfaces', 'opengever.repository.interfaces.IRepositoryFolder'),
            ('include_root', True)
        ]

        browser.open(
            self.private_dossier.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            self.repository_root.UID(),
            browser.json.get('tree')[0].get('uid'))

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
    def test_raises_bad_request_when_root_not_found(self, browser):
        self.login(self.workspace_member, browser)
        params = [
            ('root_interface', 'opengever.base.interfaces.IGeverUI'),
        ]

        with browser.expect_http_error(400):
            browser.open(
                self.repository_root.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
                headers={'Accept': 'application/json'},
            )

        self.assertEqual(
            {"message": "No root found for interface: opengever.base.interfaces.IGeverUI",
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
    def test_navigation_is_filtered_by_review_state(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('content_interfaces', 'opengever.dossier.behaviors.dossier.IDossierMarker'),
            ('review_state', 'dossier-state-active'),
        ]

        browser.open(
            self.leaf_repofolder.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        items = flatten_tree(browser.json['tree'])
        self.assertEqual(
            ['dossier-state-active']*len(items),
            [item['review_state'] for item in items])

    @browsing
    def test_navigation_is_filtered_by_multiple_review_states(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('root_interface', 'opengever.repository.interfaces.IRepositoryFolder'),
            ('content_interfaces', 'opengever.dossier.behaviors.dossier.IDossierMarker'),
            ('review_state', 'dossier-state-inactive'),
            ('review_state', 'dossier-state-resolved'),
        ]

        browser.open(
            self.leaf_repofolder.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        items = flatten_tree(browser.json['tree'])

        self.assertEqual(
            [self.expired_dossier.UID(), self.inactive_dossier.UID()],
            [item['uid'] for item in items])

    @browsing
    def test_navigation_includes_context_branch(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('root_interface', 'opengever.repository.interfaces.IRepositoryFolder'),
            ('content_interfaces', 'opengever.dossier.behaviors.dossier.IDossierMarker'),
            ('review_state', 'dossier-state-inactive'),
            ('include_context', True)
        ]

        browser.open(
            self.subdossier2.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        items = flatten_tree(browser.json['tree'])

        self.assertEqual(
            [self.inactive_dossier.UID(), self.dossier.UID(), self.subdossier2.UID()],
            [item['uid'] for item in items])

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

    @browsing
    def test_include_the_review_state(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('content_interfaces', 'opengever.dossier.businesscase.IBusinessCaseDossier')
        ]
        browser.open(
            self.portal.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json['tree'][0]['review_state'],
            'dossier-state-active',
        )

    @browsing
    def test_includes_is_subdossier(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('content_interfaces', 'opengever.dossier.businesscase.IBusinessCaseDossier')
        ]
        browser.open(
            self.portal.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        self.assertFalse(
            browser.json.get('tree')[0]['is_subdossier'],
            'The dossier "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8"'
            'is not a subdossier',
        )
        self.assertTrue(
            browser.json.get('tree')[0]['nodes'][0]['is_subdossier'],
            'The dossier "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9" '
            'is a subdossier.',
        )

    @browsing
    def test_includes_dossier_type(self, browser):
        self.login(self.regular_user, browser)

        MockDossierTypes.install()
        IDossier(self.resolvable_dossier).dossier_type = 'project'
        self.resolvable_dossier.reindexObject(idxs=['dossier_type'])
        self.commit_solr()

        params = [
            ('content_interfaces', 'opengever.dossier.businesscase.IBusinessCaseDossier')
        ]
        browser.open(
            self.portal.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)

        resolvable_dossier_node = browser.json.get('tree')[0]

        self.assertEqual('project', resolvable_dossier_node['dossier_type'])
        self.assertIsNone(resolvable_dossier_node['nodes'][0]['dossier_type'])

    @browsing
    def test_navigation_deals_properly_with_missing_value(self, browser):
        self.login(self.regular_user, browser)

        # Prep a repofolder with Missing.Value for its 'is_subdossier' metadata
        # (because tuples are immutable, this needs to be done by replacing
        # the metadata tuple with a new one consisting of left side, new value
        # and right side)
        brain = obj2brain(self.branch_repofolder)
        rid = brain.getRID()
        catalog = api.portal.get_tool('portal_catalog')
        md_pos = catalog._catalog.schema['is_subdossier']

        md = catalog._catalog.data[rid]
        catalog._catalog.data[rid] = md[:md_pos] + (Missing.Value, ) + md[md_pos + 1:]

        url = self.portal.absolute_url() + '/@navigation'
        browser.open(
            url,
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'tree', browser.json)
        self.assertEqual(
            browser.json['@id'],
            u'http://nohost/plone/@navigation')

    @browsing
    def test_navigation_titles_are_translated(self, browser):
        self.login(self.regular_user, browser)

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.supported_langs = ['de-ch', 'fr-ch']

        url = self.portal.absolute_url() + '/@navigation'
        browser.open(
            url,
            headers={
                'Accept': 'application/json',
                'Accept-Language': 'fr-ch',
            },
        )

        self.assertEqual(browser.status_code, 200)

        tree = browser.json['tree']
        expected = [
            u"1. Direction",
            u"1.1. Contrats et accords",
            u"2. Commission de v\xe9rification",
            u"3. Toile d'araign\xe9e",
        ]
        actual = [
            tree[0]['text'],
            tree[0]['nodes'][0]['text'],
            tree[1]['text'],
            tree[2]['text'],
        ]
        self.assertEqual(expected, actual)

    @browsing
    def test_navigation_excludes_trashed_objects(self, browser):
        self.login(self.regular_user, browser)
        params = [
            ('content_interfaces', 'opengever.document.document.IDocumentSchema'),
        ]

        browser.open(
            self.dossier.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        items_count_before_trash = len(flatten_tree(browser.json['tree']))

        ITrasher(self.document).trash()
        self.commit_solr()

        browser.open(
            self.dossier.absolute_url() + '/@navigation?{}'.format(urlencode(params)),
            headers={'Accept': 'application/json'},
        )
        items_count_after_trash = len(flatten_tree(browser.json['tree']))

        self.assertEqual(items_count_before_trash - 1, items_count_after_trash)
