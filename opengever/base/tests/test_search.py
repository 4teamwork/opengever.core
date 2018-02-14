from ftw.builder import Builder
from ftw.builder import create
from ftw.solr.connection import SolrResponse
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.schema import SolrSchema
from ftw.testbrowser import browsing
from mock import MagicMock
from opengever.base.interfaces import ISearchSettings
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import getUtility
import os.path


class TestOpengeverSearch(FunctionalTestCase):

    def test_types_filters_list_is_limited_to_main_types(self):
        create(Builder('repository'))
        create(Builder('repository_root'))
        create(Builder('dossier'))
        create(Builder('document'))
        create(Builder('mail'))
        create(Builder('task'))
        create(Builder('inbox'))
        create(Builder('forwarding'))
        create(Builder('contactfolder'))
        create(Builder('contact'))

        self.assertItemsEqual(
            ['opengever.task.task', 'ftw.mail.mail',
             'opengever.document.document', 'opengever.inbox.forwarding',
             'opengever.dossier.businesscasedossier'],
            self.portal.unrestrictedTraverse('@@search').types_list())

    @browsing
    def test_batch_size_is_set_to_25(self, browser):
        for i in range(0, 30):
            create(Builder('dossier').titled(u'Test'))

        browser.login().open(self.portal, view='search')
        self.assertEqual(25, len(browser.css('dl.searchResults dt')))

    @browsing
    def test_sorting_on_relevance_is_handled_correctly(self, browser):
        create(Builder('dossier').titled(u'Test A'))
        create(Builder('dossier').titled(u'Test B'))

        browser.login().open(self.portal, view='@@search?sort_on=relevance')

        self.assertEqual(['Test A', 'Test B'],
                         browser.css('.searchItem dt').text)

    @browsing
    def test_no_bubmlebee_preview_rendered_when_feature_not_enabled(self, browser):
        browser.login().open(self.portal, view='search')
        self.assertEqual(0, len(browser.css('.searchImage')))


class TestBumblebeePreview(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_thumbnails_are_linked_to_bumblebee_overlay(self, browser):
        document = create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content())

        browser.login().open(self.portal, view='search')
        browser.fill({'Search Site': 'Foo Document'}).submit()

        self.assertEqual(
            'showroom-id-{}'.format(IUUID(document)),
            browser.css('.bumblebeeSearchPreview').first.get('data-showroom-id'))

    @browsing
    def test_all_links_including_documents_are_linked_to_absolute_url(self, browser):
        dossier = create(Builder('dossier')
                         .titled(u'Foo Dossier'))
        document = create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content()
               .within(dossier))

        browser.login().open(self.portal, view='search')
        browser.fill({'SearchableText': 'Foo*'}).submit()

        dossierlink, documentlink, hiddenlink = browser.css('.searchItem dt a')

        self.assertEqual('Foo Dossier', dossierlink.text)
        self.assertEqual(dossier.absolute_url(), dossierlink.get('href'))
        self.assertEqual('contenttype-opengever-dossier-businesscasedossier',
                         dossierlink.get('class'))

        self.assertEqual('Foo Document', documentlink.text)
        self.assertEqual(document.absolute_url(), documentlink.get('href'))
        self.assertEqual('document_link icon-doc',
                         documentlink.get('class'))

    @browsing
    def test_batch_size_is_available_in_template(self, browser):
        dossier = create(Builder('dossier')
                         .titled(u'Foo Dossier'))
        create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content()
               .within(dossier))

        browser.login().open(self.portal, view='search')
        batch_size = browser.css('#search-results').first.attrib.get('data-batch-size')

        self.assertEqual(
            25, int(batch_size),
            'The batch-size data atribute should be on the tag')

    @browsing
    def test_number_of_documents_is_available_in_template(self, browser):
        dossier = create(Builder('dossier')
                         .titled(u'Foo Dossier'))

        create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content()
               .within(dossier))

        create(Builder('dossier').within(dossier))

        browser.login().open(self.portal, view='search')

        number_of_documents = browser.css(
            '#search-results .searchResults').first.attrib.get('data-number-of-documents')

        self.assertEqual(
            1, int(number_of_documents),
            'The number_of_documents data should be set to the amount of'
            'of found bumblebeeable objects.')

    @browsing
    def test_set_showroom_vars_correctly(self, browser):
        catalog = api.portal.get_tool('portal_catalog')

        base = create(Builder('dossier'))

        search_view = getMultiAdapter((self.portal, self.request), name="search")

        # Batch 1
        create(Builder('document').within(base).titled(u'A Foo'))
        create(Builder('dossier').within(base).titled(u'B Foo'))

        # Batch 2
        create(Builder('document').within(base).titled(u'C Foo'))
        create(Builder('document').within(base).titled(u'D Foo'))

        # Batch 3
        create(Builder('dossier').within(base).titled(u'E Foo'))
        create(Builder('document').within(base).titled(u'F Foo'))

        brains = catalog({'sort_on': 'sortable_title', 'SearchableText':"Foo"})

        search_view.calculate_showroom_configuration(IContentListing(brains[:2]))
        self.assertEqual(1, search_view.number_of_documents)
        self.assertEqual(0, search_view.offset)

        search_view.calculate_showroom_configuration(IContentListing(brains[2:4]))
        self.assertEqual(2, search_view.number_of_documents)
        self.assertEqual(0, search_view.offset)

        search_view.calculate_showroom_configuration(IContentListing(brains[4:]))
        self.assertEqual(1, search_view.number_of_documents)
        self.assertEqual(0, search_view.offset)


class TestSolrSearch(IntegrationTestCase):

    def setUp(self):
        super(TestSolrSearch, self).setUp()
        self.search = self.portal.unrestrictedTraverse('@@search')
        conn = MagicMock(name='SolrConnection')
        schema_resp = open(os.path.join(
            os.path.dirname(__file__), 'data', 'solr_schema.json'), 'r').read()
        conn.get = MagicMock(name='get', return_value=SolrResponse(
            body=schema_resp, status=200))
        manager = MagicMock(name='SolrConnectionManager')
        manager.connection = conn
        manager.schema = SolrSchema(manager)
        solr = getUtility(ISolrSearch)
        solr._manager = manager
        search_resp = open(os.path.join(
            os.path.dirname(__file__), 'data', 'solr_search.json'), 'r').read()
        solr.search = MagicMock(name='search', return_value=SolrResponse(
            body=search_resp, status=200))
        self.solr = solr

    def test_solr_filters_ignores_searchabletext(self):
        self.request.form.update({'SearchableText': 'foo'})
        self.assertEqual(self.search.solr_filters(), [])

    def test_solr_filters_ignores_fields_not_in_schema(self):
        self.request.form.update({'myfield': 'foo'})
        self.assertEqual(self.search.solr_filters(), [])

    def test_solr_filters_handles_date_min_records(self):
        self.request.environ['QUERY_STRING'] = (
            'created.query:record:list:date=2018-01-20&'
            'created.range:record=min')
        self.request.processInputs()
        self.assertEqual(
            self.search.solr_filters(),
            [u'created:[2018\\-01\\-20T00\\:00\\:00Z TO *]'])

    def test_solr_filters_handles_date_max_records(self):
        self.request.environ['QUERY_STRING'] = (
            'created.query:record:list:date=2018-01-20&'
            'created.range:record=max')
        self.request.processInputs()
        self.assertEqual(
            self.search.solr_filters(),
            [u'created:[* TO 2018\\-01\\-20T00\\:00\\:00Z]'])

    def test_solr_filters_handles_date_range_records(self):
        self.request.environ['QUERY_STRING'] = (
            'created.query:record:list:date=2018-01-20&'
            'created.query:record:list:date=2018-01-25&'
            'created.range:record=minmax')
        self.request.processInputs()
        self.assertEqual(
            self.search.solr_filters(),
            [u'created:[2018\\-01\\-20T00\\:00\\:00Z TO 2018\\-01\\-25T00\\:00\\:00Z]'])

    def test_solr_filters_handles_lists(self):
        self.request.environ['QUERY_STRING'] = (
            'portal_type:list=opengever.document.document&'
            'portal_type:list=opengever.dossier.businesscasedossier')
        self.request.processInputs()
        self.assertEqual(
            self.search.solr_filters(),
            [u'portal_type:(opengever.document.document OR '
             u'opengever.dossier.businesscasedossier)'])

    def test_solr_filters_handles_simple_values(self):
        self.request.environ['QUERY_STRING'] = (
            'sequence_number:int=123&responsible=hans.muster')
        self.request.processInputs()
        self.assertEqual(
            self.search.solr_filters(),
            [u'responsible:hans.muster', u'sequence_number:123'])

    def test_solr_sort_on_date(self):
        self.request.environ['QUERY_STRING'] = (
            'sort_on=Date&sort_order=reverse')
        self.request.processInputs()
        self.assertEqual(self.search.solr_sort(), u'modified desc')

    def test_solr_sort_on_title(self):
        self.request.environ['QUERY_STRING'] = (
            'sort_on=sortable_title')
        self.request.processInputs()
        self.assertEqual(self.search.solr_sort(), u'sortable_title asc')

    def test_solr_sort_on_relevance(self):
        self.request.environ['QUERY_STRING'] = (
            'sort_on=relevance')
        self.request.processInputs()
        self.assertEqual(self.search.solr_sort(), None)

    def test_solr_results_with_searchable_text(self):
        self.request.environ['QUERY_STRING'] = ('SearchableText=foo')
        self.request.processInputs()
        self.search.solr_results()
        self.solr.search.assert_called_with(
            query=(u'{!boost b=recip(ms(NOW,modified),3.858e-10,10,1)}'
                   u'Title:foo^100 OR Title:foo*^10 OR SearchableText:foo^10 '
                   u'OR SearchableText:foo* '
                   u'OR sequence_number_string:foo^2000'),
            filters=[u'trashed:false'],
            start=0,
            rows=10,
            sort=None,
            **{
                'fl': [
                    'UID', 'Title', 'getIcon', 'portal_type', 'path',
                    'containing_dossier', 'id', 'created', 'modified',
                    'review_state', 'bumblebee_checksum',
                ],
                'hl': 'on',
                'hl.fl': 'SearchableText',
                'hl.snippets': 3,
            })

    def test_solr_results_with_filter(self):
        self.request.environ['QUERY_STRING'] = 'responsible=hans.muster'
        self.request.processInputs()
        self.search.solr_results()
        self.solr.search.assert_called_with(
            query=u'*:*',
            filters=[u'responsible:hans.muster', u'trashed:false'],
            start=0,
            rows=10,
            sort=None,
            **{
                'fl': [
                    'UID', 'Title', 'getIcon', 'portal_type', 'path',
                    'containing_dossier', 'id', 'created', 'modified',
                    'review_state', 'bumblebee_checksum',
                ],
                'hl': 'on',
                'hl.fl': 'SearchableText',
                'hl.snippets': 3,
            })

    def test_search_uses_solr_if_enabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        settings.use_solr = True
        self.request.environ['QUERY_STRING'] = ('SearchableText=foo')
        self.request.processInputs()
        self.search.results()
        self.assertTrue(self.solr.search.called)

    def test_search_doesnt_use_solr_if_disabled(self):
        self.request.environ['QUERY_STRING'] = ('SearchableText=foo')
        self.request.processInputs()
        self.search.results()
        self.assertFalse(self.solr.search.called)
