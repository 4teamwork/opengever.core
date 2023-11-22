from ftw.testbrowser import browsing
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import MockDossierTypes
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from zope.interface import directlyProvides


class TestBreadcrumbsSerialization(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_plone_site_has_no_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal.absolute_url() + '/@breadcrumbs', headers=self.api_headers)
        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/@breadcrumbs',
                u'items': [],
            },
            browser.json
        )

    @browsing
    def test_breadcrumbs_payload(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root.absolute_url() + '/@breadcrumbs', headers=self.api_headers)
        self.assertEqual(
            [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem',
                    u'@type': u'opengever.repository.repositoryroot',
                    u'UID': u'createrepositorytree000000000001',
                    u'description': u'',
                    u'is_leafnode': None,
                    u'review_state': u'repositoryroot-state-active',
                    u'title': u'Ordnungssystem',
                }
            ],
            browser.json['items']
        )

    @browsing
    def test_plone_site_is_not_in_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root.absolute_url() + '/@breadcrumbs', headers=self.api_headers)
        self.assertEqual(
            [u'http://nohost/plone/ordnungssystem'],
            [item['@id'] for item in browser.json['items']]
        )

    @browsing
    def test_breadcrumbs_contain_context(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.branch_repofolder.absolute_url() + '/@breadcrumbs', headers=self.api_headers)
        self.assertEqual(
            [
                u'http://nohost/plone/ordnungssystem',
                u'http://nohost/plone/ordnungssystem/fuhrung',
            ],
            [item['@id'] for item in browser.json['items']]
        )

    @browsing
    def test_breadcrumbs_are_sorted_by_ancestors(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document.absolute_url() + '/@breadcrumbs', headers=self.api_headers)
        self.assertEqual(
            [
                u'http://nohost/plone/ordnungssystem',
                u'http://nohost/plone/ordnungssystem/fuhrung',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
            ],
            [item['@id'] for item in browser.json['items']]
        )

    @browsing
    def test_objs_can_be_hidden_from_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)
        directlyProvides(self.leaf_repofolder, IHideFromBreadcrumbs)
        browser.open(self.document.absolute_url() + '/@breadcrumbs', headers=self.api_headers)
        self.assertEqual(
            [
                u'http://nohost/plone/ordnungssystem',
                u'http://nohost/plone/ordnungssystem/fuhrung',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
            ],
            [item['@id'] for item in browser.json['items']]
        )

    @browsing
    def test_is_subdossier_in_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.subdocument.absolute_url() + '/@breadcrumbs', headers=self.api_headers)

        # self.leaf_repofolder: Unable to determine subdossier status.
        self.assertIsNone(getattr(self.leaf_repofolder, 'is_subdossier', None))
        self.assertNotIn('is_subdossier', browser.json['items'][2])

        # self.dossier: Not a subdossier.
        self.assertFalse(self.dossier.is_subdossier())
        self.assertFalse(browser.json['items'][3]['is_subdossier'])

        # self.subdossier: This is a subdossier.
        self.assertTrue(self.subdossier.is_subdossier())
        self.assertTrue(browser.json['items'][4]['is_subdossier'])

    @browsing
    def test_dossier_type_in_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)

        MockDossierTypes.install()
        IDossier(self.dossier).dossier_type = 'project'

        browser.open(self.subdocument.absolute_url() + '/@breadcrumbs',
                     headers=self.api_headers)

        # self.leaf_repofolder: No dossier_type
        self.assertNotIn('dossier_type', browser.json['items'][2])

        # self.dossier: Has a dossier type
        self.assertEqual('project', browser.json['items'][3]['dossier_type'])

        # self.subdossier: Has default dossier type (None).
        self.assertIsNone(browser.json['items'][4]['dossier_type'])

    @browsing
    def test_is_leafnode_in_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.subdocument.absolute_url() + '/@breadcrumbs', headers=self.api_headers)

        # self.repository_root: Unable to determine leaf node status.
        self.assertIsNone(getattr(self.repository_root, 'is_leaf_node', None))
        self.assertIsNone(browser.json['items'][0]['is_leafnode'])

        # self.branch_repofolder: Not a leaf node.
        self.assertFalse(self.branch_repofolder.is_leaf_node())
        self.assertFalse(browser.json['items'][1]['is_leafnode'])

        # self.leaf_repofolder: This is a leaf node.
        self.assertTrue(self.leaf_repofolder.is_leaf_node())
        self.assertTrue(browser.json['items'][2]['is_leafnode'])

    @browsing
    def test_expanded_breadcrumbs_in_components(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.branch_repofolder.absolute_url() + '?expand=breadcrumbs', headers=self.api_headers)
        self.assertEqual(
            [
                {
                    u'description': u'',
                    u'title': u'Ordnungssystem',
                    u'is_leafnode': None,
                    u'review_state': u'repositoryroot-state-active',
                    u'@id': u'http://nohost/plone/ordnungssystem',
                    u'@type': u'opengever.repository.repositoryroot',
                    u'UID': u'createrepositorytree000000000001',
                },
                {
                    u'description': u'Alles zum Thema F\xfchrung.',
                    u'title': u'1. F\xfchrung',
                    u'is_leafnode': False,
                    u'review_state': u'repositoryfolder-state-active',
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung',
                    u'@type': u'opengever.repository.repositoryfolder',
                    u'UID': u'createrepositorytree000000000002',
                },
            ],
            browser.json['@components']['breadcrumbs']['items']
        )

    @browsing
    def test_is_subtasktemplatefolder_in_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.tasktemplate.absolute_url() + '/@breadcrumbs',
                     headers=self.api_headers)

        self.assertIsNone(getattr(self.templates, 'is_subtasktemplatefolder', None))
        self.assertNotIn('is_subtasktemplatefolder', browser.json['items'][0])

        self.assertFalse(self.tasktemplatefolder.is_subtasktemplatefolder())
        self.assertFalse(browser.json['items'][1]['is_subtasktemplatefolder'])
