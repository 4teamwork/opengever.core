from opengever.base.interfaces import ISearchSettings
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.catalog_source import BatchableSolrResults
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
        self.source.solr_results({'SearchableText': 'foo bar'})
        self.assertEqual(
            self.solr.search.call_args[1]['query'],
            u'foo bar'
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

    def test_solr_filters_contain_path_depth(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'path': {'query': '/my/path', 'depth': '1'}})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false',
             u'path_parent:\\/my\\/path',
             u'path_depth:[* TO 3]'])

    def test_solr_filters_handle_booleans(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'is_subdossier': True})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false', u'is_subdossier:true'])

    def test_solr_filters_handle_strings(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'metadata': 'FD 1 / 1'})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false', u'metadata:FD 1 \\/ 1'])

    def test_solr_filters_ignore_unknown_fields(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'reference_number': 'FD 1 / 1'})
        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            [u'trashed:false'])

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

    def test_solr_sort_ignores_unknown_fields(self):
        self.source.solr_results(
            {'SearchableText': 'foo', 'sort_on': 'getObjPositionInParent'})
        self.assertEqual(
            self.solr.search.call_args[1]['sort'],
            None)

    def test_solr_fieldlist_contains_columns(self):
        self.source.config.columns = (
            {'column': 'reference'},
            {'column': 'Title'},
        )
        self.source.solr_results({'SearchableText': 'foo'})
        self.assertEqual(
            self.solr.search.call_args[1]['fl'],
            ['UID', 'getIcon', 'portal_type', 'path', 'id',
             'bumblebee_checksum', 'reference', 'Title']
            )

    def test_solr_start_is_calculated_from_batching_current_page_and_pagesize(self):
        self.source.solr_results(
            {'SearchableText': 'foo'})
        self.assertEqual(
            self.solr.search.call_args[1]['start'],
            0)

        self.source.config.batching_current_page = 3
        self.source.config.pagesize = 15
        self.source.solr_results(
            {'SearchableText': 'foo'})
        self.assertEqual(
            self.solr.search.call_args[1]['start'],
            30)

    def test_solr_rows_equals_pagesize(self):
        self.source.solr_results(
            {'SearchableText': 'foo'})
        self.assertEqual(
            self.solr.search.call_args[1]['rows'],
            50)

        self.source.config.pagenumber = 3
        self.source.config.pagesize = 15
        self.source.solr_results(
            {'SearchableText': 'foo'})
        self.assertEqual(
            self.solr.search.call_args[1]['rows'],
            15)

    def test_solr_is_used_if_enabled_and_searchable_text(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        settings.use_solr = True
        self.source.search_results({'SearchableText': 'foo'})
        self.assertTrue(self.solr.search.called)

    def test_solr_is_not_used_if_disabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        settings.use_solr = False
        self.source.search_results({'SearchableText': 'foo'})
        self.assertFalse(self.solr.search.called)

    def test_solr_is_used_if_enabled_and_without_searchable_text(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        settings.use_solr = True
        self.source.search_results({})
        self.assertTrue(self.solr.search.called)


class TestBatchableSolrResults(IntegrationTestCase):

    def setUp(self):
        super(TestBatchableSolrResults, self).setUp()
        self.solr = self.mock_solr('solr_search.json')

    def test_solr_results_for_first_batch(self):
        resp = self.solr.search()
        results = BatchableSolrResults(resp)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].id, 'my-folder-1')
        self.assertEqual(results[1].id, 'my-folder-2')
        self.assertEqual(results[2].id, 'my-document')

    def test_solr_results_for_subsequent_batch(self):
        resp = self.solr.search()
        resp.num_found = 53
        resp.start = 50
        results = BatchableSolrResults(resp)
        self.assertEqual(len(results), 53)
        self.assertEqual(results[50].id, 'my-folder-1')
        self.assertEqual(results[51].id, 'my-folder-2')
        self.assertEqual(results[52].id, 'my-document')

    def test_solr_results_are_sliceable(self):
        resp = self.solr.search()
        resp.num_found = 53
        resp.start = 50
        results = BatchableSolrResults(resp)
        self.assertEqual(
            ['my-folder-1', 'my-folder-2', 'my-document'],
            [r.id for r in results[50:]],
        )
