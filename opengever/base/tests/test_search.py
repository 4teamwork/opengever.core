from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter


class TestOpengeverSearch(IntegrationTestCase):

    features = ('!solr', )

    def test_types_filters_list_is_limited_to_main_types(self):
        self.login(self.regular_user)

        self.assertItemsEqual(
            ['opengever.task.task', 'ftw.mail.mail',
             'opengever.document.document', 'opengever.inbox.forwarding',
             'opengever.dossier.businesscasedossier'],
            self.portal.unrestrictedTraverse('@@search').types_list())

    @browsing
    def test_batch_size_is_set_to_25(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='@@search')

        self.assertEqual(25, len(browser.css('dl.searchResults dt')))

    @browsing
    def test_sorting_on_relevance_is_handled_correctly(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search')

        self.assertEqual(25, len(browser.css('dl.searchResults dt')))

    @browsing
    def test_no_bubmlebee_preview_rendered_when_feature_not_enabled(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search?SearchableText=vertrag')

        self.assertEqual(0, len(browser.css('.searchImage')))

    @browsing
    def test_prefill_from_advanced_search_omits_searchable_text_keywords(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.portal,
            view='advanced_search?SearchableText=foo+NOT+bar+AND+qwe+OR+asd+AND+zxc+OR+dsa+NOT+rsa')

        prefill = browser.css('#searchGadget').first.value
        self.assertNotIn('AND', prefill)
        self.assertNotIn('OR', prefill)
        self.assertNotIn('NOT', prefill)

    @browsing
    def test_advanced_search_link_is_url_encoded(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search?SearchableText=M\xc3\xbcller and {co)')

        advanced_search = browser.find("Advanced Search")
        expected_url = (self.portal.absolute_url() +
                        '/advanced_search?SearchableText=M%C3%BCller+and+%7Bco%29')

        self.assertEqual(expected_url, advanced_search.get("href"))

    @browsing
    def test_workspace_meeting_agendaitems_are_excluded_from_search(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.portal, view='@@search?UID={}'.format(
            self.workspace_meeting_agenda_item.UID()))
        self.assertEqual(0, len(browser.css('dl.searchResults dt')))


class TestOpengeverSearchSolr(SolrIntegrationTestCase):

    def test_types_filters_list_is_limited_to_main_types(self):
        self.login(self.regular_user)

        self.assertItemsEqual(
            ['opengever.task.task', 'ftw.mail.mail',
             'opengever.document.document', 'opengever.inbox.forwarding',
             'opengever.dossier.businesscasedossier'],
            self.portal.unrestrictedTraverse('@@search').types_list())

    @browsing
    def test_batch_size_is_set_to_25(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='@@search')

        self.assertEqual(25, len(browser.css('dl.searchResults dt')))

    @browsing
    def test_sorting_on_relevance_is_handled_correctly(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search')

        self.assertEqual(25, len(browser.css('dl.searchResults dt')))

    @browsing
    def test_no_bubmlebee_preview_rendered_when_feature_not_enabled(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search?SearchableText=vertrag')

        self.assertEqual(0, len(browser.css('.searchImage')))

    @browsing
    def test_prefill_from_advanced_search_omits_searchable_text_keywords(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.portal,
            view='advanced_search?SearchableText=foo+NOT+bar+AND+qwe+OR+asd+AND+zxc+OR+dsa+NOT+rsa')

        prefill = browser.css('#searchGadget').first.value
        self.assertNotIn('AND', prefill)
        self.assertNotIn('OR', prefill)
        self.assertNotIn('NOT', prefill)

    @browsing
    def test_advanced_search_link_is_url_encoded(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search?SearchableText=M\xc3\xbcller and {co)')

        advanced_search = browser.find("Advanced Search")
        expected_url = (self.portal.absolute_url() +
                        '/advanced_search?SearchableText=M%C3%BCller+and+%7Bco%29')

        self.assertEqual(expected_url, advanced_search.get("href"))


class TestBumblebeePreview(SolrIntegrationTestCase):

    features = ('bumblebee', )

    @browsing
    def test_thumbnails_are_linked_to_bumblebee_overlay(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@@search?portal_type=opengever.document.document&sort_on=created')

        self.assertEqual(
            'showroom-id-{}'.format(IUUID(self.asset_template)),
            browser.css('.bumblebeeSearchPreview').first.get('data-showroom-id'))

    @browsing
    def test_all_links_including_documents_are_linked_to_absolute_url(self, browser):
        self.login(self.regular_user, browser=browser)

        self.dossier.title = 'Foosearch Dossier'
        self.document.title = 'Foosearch Document'
        [obj.reindexObject() for obj in [self.dossier, self.document]]
        self.commit_solr()

        browser.open(self.portal, view='@@search?SearchableText=Foosearch&sort_on=modified')
        dossierlink, documentlink, hiddenlink = browser.css('.searchItem dt a')

        self.assertEqual('Foosearch Dossier', dossierlink.text)
        self.assertEqual(self.dossier.absolute_url(), dossierlink.get('href'))
        self.assertEqual('contenttype-opengever-dossier-businesscasedossier',
                         dossierlink.get('class'))

        self.assertEqual('Foosearch Document', documentlink.text)
        self.assertEqual(self.document.absolute_url(), documentlink.get('href'))
        self.assertEqual('document_link icon-docx',
                         documentlink.get('class'))

    @browsing
    def test_batch_size_is_available_in_template(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search')

        batch_size = browser.css('#search-results').first.attrib.get('data-batch-size')
        self.assertEqual(
            25, int(batch_size),
            'The batch-size data atribute should be on the tag')

    @browsing
    def test_number_of_documents_is_available_in_template(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search?SearchableText=kommentar')

        number_of_documents = browser.css(
            '#search-results .searchResults').first.attrib.get('data-number-of-documents')
        self.assertEqual(
            1, int(number_of_documents),
            'The number_of_documents data should be set to the amount of'
            'of found bumblebeeable objects.')

    @browsing
    def test_set_showroom_vars_correctly(self, browser):
        self.login(self.regular_user, browser=browser)

        catalog = api.portal.get_tool('portal_catalog')
        search_view = getMultiAdapter((self.portal, self.request), name="search")

        brains = catalog({'portal_type': 'opengever.document.document',
                          'sort_on': 'sortable_title',
                          'SearchableText': "Foo"})

        brains = [obj2brain(obj) for obj in
                  [self.document, self.dossier, self.subdocument]]
        search_view.calculate_showroom_configuration(IContentListing(brains))
        self.assertEqual(2, search_view.number_of_documents)
        self.assertEqual(0, search_view.offset)

        brains = [obj2brain(obj) for obj in
                  [self.task, self.subdossier]]
        search_view.calculate_showroom_configuration(IContentListing(brains))
        self.assertEqual(0, search_view.number_of_documents)
        self.assertEqual(0, search_view.offset)


class TestSolrSearch(IntegrationTestCase):

    def setUp(self):
        super(TestSolrSearch, self).setUp()

        self.search = self.portal.unrestrictedTraverse('@@search')
        self.solr = self.mock_solr('solr_search.json')

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

    def test_solr_filters_switch_path_to_parent_path(self):
        self.request.environ['QUERY_STRING'] = (
            'sequence_number:int=123&path=/fd/ordnungssystem')
        self.request.processInputs()
        self.assertEqual(
            self.search.solr_filters(),
            [u'path_parent:\\/fd\\/ordnungssystem', u'sequence_number:123'])

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
                   u'Title:foo^100 OR Title:foo*^20 OR SearchableText:foo^5 '
                   u'OR SearchableText:foo* OR metadata:foo^10 '
                   u'OR metadata:foo*^2 OR sequence_number_string:foo^2000'),
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
                'hl.encoder': 'html',
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
                'hl.encoder': 'html',
                'hl.snippets': 3,
            })

    def test_search_uses_solr_if_enabled(self):
        self.request.environ['QUERY_STRING'] = ('SearchableText=foo')
        self.request.processInputs()
        self.search.results()
        self.assertTrue(self.solr.search.called)

    def test_search_doesnt_use_solr_if_disabled(self):
        self.deactivate_feature('solr')
        self.request.environ['QUERY_STRING'] = ('SearchableText=foo')
        self.request.processInputs()
        self.search.results()
        self.assertFalse(self.solr.search.called)

    def test_solr_does_not_modify_request_form(self):
        self.request.environ['QUERY_STRING'] = 'SearchableText=foo&review_state:list=dossier-state-active&review_state:list=dossier-state-inactive'

        self.request.processInputs()
        self.search.solr_results()

        self.assertEquals(
            {'SearchableText': 'foo',
             'review_state': ['dossier-state-active', 'dossier-state-inactive']},
            self.request.form)

    @browsing
    def test_show_more_is_not_rendered_per_default(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal, view='@@livesearch_reply?q=test')
        self.assertIsNone(browser.find('Show all items'))

    @browsing
    def test_path_for_show_more_is_not_none(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal, view='@@livesearch_reply?q=test&limit=2')
        all_items_link = browser.find('Show all items')
        self.assertIsNotNone(all_items_link)
        self.assertEqual(
            '<a class="dropdown-list-item LSRow" href="@@search?SearchableText=test&amp;path=/plone">Show all items</a>',
            all_items_link.outerHTML,
            )

    @browsing
    def test_advanced_search_link_is_url_encoded(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@@search?SearchableText=M\xc3\xbcller and {co)')

        advanced_search = browser.find("Advanced Search")
        expected_url = (self.portal.absolute_url() +
                        '/advanced_search?SearchableText=M%C3%BCller+and+%7Bco%29')

        self.assertEqual(expected_url, advanced_search.get("href"))
