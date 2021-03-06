from ftw.testbrowser import browsing
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from opengever.testing.integration_test_case import SolrIntegrationTestCase
from plone.uuid.interfaces import IUUID
from unittest import skip


class TestMockSolrSearchGet(IntegrationTestCase):

    features = ['solr']

    @browsing
    def test_default_sort(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json={})

        url = u'{}/@solrsearch?q=Foo&fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['sort'], 'score desc')

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['sort'], None)


class TestSolrSearchGet(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')

    @browsing
    def test_raises_bad_request_if_solr_is_not_enabled(self, browser):
        self.deactivate_feature('solr')

        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = u'{}/@solrsearch'.format(self.portal.absolute_url())
            browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Solr is not enabled on this GEVER installation.',
             u'type': u'BadRequest'}, browser.json)

    @browsing
    def test_raises_internal_error_for_invalid_queries(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(500):
            url = u'{}/@solrsearch?q=OR'.format(self.portal.absolute_url())
            browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(u'InternalError', browser.json['type'])

    @browsing
    def test_simple_search_query(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(3, browser.json["items_total"])
        self.assertItemsEqual(
            [item.absolute_url() for item in
             (self.document, self.subdocument, self.offered_dossier_to_archive)],
            [item["@id"] for item in browser.json[u'items']])

    @browsing
    def test_raw_query(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q.raw=Title:Kommentar'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(1, browser.json["items_total"])
        self.assertEqual(self.proposaldocument.absolute_url(),
                         browser.json["items"][0]["@id"])

    @browsing
    def test_fallback_to_default_fields_if_fl_parameter_is_empty(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual([u'review_state',
                               u'title',
                               u'@id',
                               u'UID',
                               u'@type',
                               u'description'],
                              browser.json["items"][0].keys())

    @browsing
    def test_blacklisted_attributes_are_skipped(self, browser):
        self.login(self.regular_user, browser=browser)

        # SearchableText is an unsupported field
        url = u'{}/@solrsearch?fl=SearchableText,allowedRolesAndUsers,getObject,UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual([u'UID', u'Title'],
                              browser.json['items'][0].keys())

    @browsing
    def test_searches_in_context_if_path_is_not_specified(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.subdossier.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        search_on_context = browser.json

        self.assertEqual(5, search_on_context['items_total'])
        for doc in search_on_context['items']:
            self.assertIn(self.subdossier.absolute_url(), doc['@id'])

        url = u'{}/@solrsearch?fq=path:{}'.format(
            self.portal.absolute_url(), self.subdossier.absolute_url_path())
        browser.open(url, method='GET', headers=self.api_headers)
        search_with_path = browser.json

        self.assertEqual(search_on_context['items_total'],
                         search_with_path['items_total'])
        self.assertEqual(search_on_context['items'],
                         search_with_path['items'])

    @browsing
    def test_search_respects_depth_parameter(self, browser):
        self.login(self.regular_user, browser=browser)

        base_url = u'{}/@solrsearch?'\
            'fq=portal_type:opengever.dossier.businesscasedossier'.format(
                self.dossier.absolute_url())
        browser.open(
            "{}&depth=2".format(base_url),
            method='GET',
            headers=self.api_headers)

        self.assertEqual(3, browser.json['items_total'])
        self.assertItemsEqual(
            [self.subdossier.absolute_url(),
             self.subdossier2.absolute_url(),
             self.subsubdossier.absolute_url()],
            [doc['@id'] for doc in browser.json['items']])

        browser.open(
            "{}&depth=1".format(base_url),
            method='GET',
            headers=self.api_headers)

        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            [self.subdossier.absolute_url(),
             self.subdossier2.absolute_url()],
            [doc['@id'] for doc in browser.json['items']])

        browser.open(
            "{}&depth=0".format(base_url),
            method='GET',
            headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        self.assertItemsEqual(
            [self.dossier.absolute_url()],
            [doc['@id'] for doc in browser.json['items']])

    @browsing
    def test_filter_queries(self, browser):
        self.login(self.regular_user, browser=browser)
        url = (u'{}/@solrsearch?q=wichtig'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)
        all_items = browser.json["items"]
        self.assertEqual(3, len(all_items))

        url = (u'{}/@solrsearch?q=wichtig&'
               u'fq=portal_type:opengever.document.document'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)
        filtered_items = browser.json["items"]
        self.assertEqual(2, len(filtered_items))
        self.assertItemsEqual(
            [item["@type"] for item in filtered_items
             if item["@type"] == 'opengever.document.document'],
            [item["@type"] for item in filtered_items])

        url = (u'{}/@solrsearch?q=wichtig&fq=portal_type:opengever.document.document&'
               u'fq=path_parent:{}'.format(
                   self.portal.absolute_url(),
                   self.subdossier.absolute_url_path().replace("/", "\\/")))
        browser.open(url, method='GET', headers=self.api_headers)
        filtered_items = browser.json["items"]
        self.assertEqual(1, len(filtered_items))
        self.assertEqual(self.subdocument.absolute_url(),
                         filtered_items[0]["@id"])

    @browsing
    def test_returns_json_serialized_solr_docs(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig&fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [{u'Title': item.title, u'UID': IUUID(item)}
             for item in (self.document, self.subdocument, self.offered_dossier_to_archive)],
            browser.json[u'items'])

    @browsing
    def test_query_for_external_reference(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=external_reference:qpr-900-9001-\xf7&fl=UID,external_reference'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [{u'UID': IUUID(self.dossier),
              u'external_reference': IDossier(self.dossier).external_reference}],
            browser.json[u'items'])

    @skip("Seems this does not behave very consistently in the moment."
          "Returns empty list in some cases, list of empty strings in others")
    @browsing
    def test_returns_snippets(self, browser):
        """Snippets do not really seem to work??
        """
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=Foo&fl=UID,Title,snippets'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            ['' for i in range(3)],
            [item["snippets"] for item in browser.json[u'items']])

    @browsing
    def test_returns_facets_with_labels(self, browser):
        self.login(self.regular_user, browser=browser)

        url = (u'{}/@solrsearch?q=wichtig&facet=true&facet.field=Subject&'
               u'facet.mincount=1'.format(self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn(u'facet_counts', browser.json)
        facet_counts = browser.json['facet_counts']
        self.assertItemsEqual([u'Subject'], facet_counts.keys())
        self.assertItemsEqual(
            {u'Wichtig': {u'count': 3, u'label': u'Wichtig'},
             u'Subkeyword': {u'count': 1, u'label': u'Subkeyword'}},
            facet_counts[u'Subject'])

    @browsing
    def test_facet_labels_are_transformed_properly(self, browser):
        self.login(self.regular_user, browser=browser)

        url = (u'{}/@solrsearch?q=wichtig&facet=on&facet.field=creator&'
               u'facet.field=responsible&facet.mincount=1'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn(u'facet_counts', browser.json)
        facet_counts = browser.json['facet_counts']

        self.assertItemsEqual([u'creator', 'responsible'], facet_counts.keys())
        self.assertItemsEqual(
            {u'robert.ziegler': {u'count': 3, u'label': u'Ziegler Robert'}},
            facet_counts[u'creator'])
        self.assertItemsEqual(
            {u'robert.ziegler': {u'count': 1, u'label': u'Ziegler Robert'}},
            facet_counts[u'responsible'])

    @browsing
    def test_using_a_solr_index_as_a_facet_works_properly(self, browser):
        self.login(self.regular_user, browser=browser)

        url = (u'{}/@solrsearch?q=wichtig&facet=on&facet.field=Creator&'
               u'facet.mincount=1'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        facet_counts = browser.json['facet_counts']

        self.assertItemsEqual(
            {u'robert.ziegler': {u'count': 3, u'label': u'robert.ziegler'}},
            facet_counts[u'Creator'])

    @browsing
    def test_default_start_and_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertTrue(browser.json["items_total"] > 25)
        self.assertEqual(25, len(browser.json["items"]))
        self.assertEqual(0, browser.json["start"])
        self.assertEqual(25, browser.json["rows"])

    @browsing
    def test_custom_start_and_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fl=UID,Title&rows=100'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        all_items = browser.json["items"]

        url = u'{}/@solrsearch?fl=UID,Title&start=20&rows=10'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        items = browser.json["items"]

        self.assertTrue(len(all_items) > 30)
        self.assertEqual(items, all_items[20:30])

    @browsing
    def test_max_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig&fl=UID,Title&start=0&rows=10000000'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1000, browser.json["rows"])

    @browsing
    def test_default_sort_by_score(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=James%20Bond&fl=Title'.format(
            self.portal.absolute_url())

        self.dossier.title = 'James Bond'
        self.dossier.reindexObject()

        self.subdossier.title = 'Agent 007'
        self.subdossier.description = 'James Bond'
        self.subdossier.reindexObject()

        self.document.title = 'James 007 Bond'
        self.document.reindexObject()

        self.commit_solr()

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual([u'James Bond',
                          u'Agent 007',
                          u'James 007 Bond'],
                         [item["Title"] for item in browser.json["items"]])

    @browsing
    def test_custom_sort(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig&fl=UID,Title,modified&sort=modified asc'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual([u'2016-08-31T14:07:33+00:00',
                          u'2016-08-31T14:21:33+00:00',
                          u'2016-08-31T19:01:33+00:00'],
                         [item["modified"] for item in browser.json["items"]])

    @browsing
    def test_review_state(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=review_state'.format(
            self.portal.absolute_url(), self.subdossier.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            u'dossier-state-active',
            browser.json['items'][0]['review_state']
        )

    @browsing
    def test_undeterminable_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_subdossier'.format(
            self.portal.absolute_url(), self.task.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIsNone(browser.json['items'][0]['is_subdossier'])

    @browsing
    def test_branch_dossier_is_not_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_subdossier'.format(
            self.portal.absolute_url(), self.dossier.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertFalse(browser.json['items'][0]['is_subdossier'])

    @browsing
    def test_subdossier_is_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_subdossier'.format(
            self.portal.absolute_url(), self.subdossier.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertTrue(browser.json['items'][0]['is_subdossier'])

    @browsing
    def test_undeterminable_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_leafnode'.format(
            self.portal.absolute_url(), self.subdocument.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIsNone(browser.json['items'][0]['is_leafnode'])

    @browsing
    def test_branch_repositoryfolder_is_not_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_leafnode'.format(
            self.portal.absolute_url(), self.branch_repofolder.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertFalse(browser.json['items'][0]['is_leafnode'])

    @browsing
    def test_leaf_repositoryfolder_is_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_leafnode'.format(
            self.portal.absolute_url(), self.leaf_repofolder.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertTrue(browser.json['items'][0]['is_leafnode'])

    @browsing
    def test_batching(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@solrsearch'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        all_items = browser.json['items']

        # batched no start point
        view = '@solrsearch?b_size=3'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_items[0:3], browser.json['items'])

        # Next batch
        browser.open(
            browser.json.get('batching').get('next'), headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_items[3:6], browser.json['items'])

        # Previous batch
        browser.open(
            browser.json.get('batching').get('prev'), headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_items[0:3], browser.json['items'])
