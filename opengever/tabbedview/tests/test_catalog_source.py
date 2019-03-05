from opengever.base.interfaces import ISearchSettings
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.catalog_source import GeverCatalogTableSource
from opengever.testing import IntegrationTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import pkg_resources

pkg_path = pkg_resources.get_distribution('opengever.core').location


class TestSolrSearch(IntegrationTestCase):

    def setUp(self):
        super(TestSolrSearch, self).setUp()

        self.solr = self.mock_solr('solr_search.json')
        self.source = GeverCatalogTableSource(
            BaseCatalogListingTab(self.portal, self.request), self.request)

    def test_solr_query_contains_searchable_text(self):
        self.source.solr_results({'SearchableText': 'foo*'})
        self.assertEqual(
            self.solr.search.call_args[1]['query'],
            u'(Title:foo* OR SearchableText:foo* OR metadata:foo* OR '
            u'Title:foo OR SearchableText:foo OR metadata:foo)'
        )

    def test_solr_query_contains_pattern_for_each_term(self):
        self.source.solr_results({'SearchableText': 'foo bar*'})
        self.assertEqual(
            self.solr.search.call_args[1]['query'],
            u'(Title:foo* OR SearchableText:foo* OR metadata:foo* OR '
            u'Title:foo OR SearchableText:foo OR metadata:foo) AND '
            u'(Title:bar* OR SearchableText:bar* OR metadata:bar* OR '
            u'Title:bar OR SearchableText:bar OR metadata:bar)'
        )

    def test_solr_filters_contain_trashed(self):
        self.source.solr_results(
            {'SearchableText': 'foo'})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false'])

    def test_solr_filters_contain_path_parent(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'path': {'query': '/my/path'}})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false', u'path_parent:\\/my\\/path'])

    def test_solr_filters_handle_booleans(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'is_subdossier': True})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false', u'is_subdossier:true'])

    def test_solr_filters_handle_strings(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'reference_number': 'FD 1 / 1'})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false', u'reference_number:FD 1 \\/ 1'])

    def test_solr_filters_do_not_contain_sort_parameters(self):
        self.source.solr_results({
            'SearchableText': 'foo',
            'sort_on': 'modified',
            'sort_order': 'descending',
            })
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false'])

    def test_solr_sort(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'sort_on': 'sortable_title'})
        self.assertEqual(
            self.solr.search.call_args[1]['sort'],
            u'sortable_title asc')

    def test_solr_fieldlist_contains_columns(self):
        self.source.config.columns = (
            {'column': 'reference'},
            {'column': 'Title'},
        )
        self.source.solr_results({'SearchableText': 'foo'})
        self.assertEqual(
            self.solr.search.call_args[1]['fl'],
            ['UID', 'getIcon', 'portal_type', 'path', 'id',
             'bumblebee_checksum', 'modified', 'reference', 'Title']
            )

    def test_solr_is_used_if_enabled_and_searchable_text(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        settings.use_solr = True
        self.source.search_results({'SearchableText': 'foo'})
        self.assertTrue(self.solr.search.called)

    def test_solr_is_not_used_if_disabled(self):
        self.source.search_results({'SearchableText': 'foo'})
        self.assertFalse(self.solr.search.called)

    def test_solr_is_used_if_enabled_and_no_searchable_text(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        settings.use_solr = True
        self.source.search_results({})
        self.assertTrue(self.solr.search.called)
