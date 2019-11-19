from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestSolrSearchGet(IntegrationTestCase):

    # TODO: Replace mock tests using a real solr as soon this
    # is possible (see #4844).

    api_headers = {'Accept': 'application/json'}
    features = ['solr']

    solr_search_response = {
        "responseHeader": {
            "status": 0,
            "QTime": 3,
            "limit": 10,
            "params": {
                "json": "{\n  \"query\": \":\"\n}"
            }
        },
        "response": {
            "numFound": 3,
            "start": 0,
            "docs": [
                {
                    "UID": "createtreatydossiers000000000001",
                    "path": "/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1",
                    "Title": "Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung",
                },
                {
                    "UID": "createexpireddossier000000000001",
                    "path": "/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5",
                    "Title": "Abgeschlossene Vertr\xc3\xa4ge",
                },
                {
                    "UID": "createtreatydossiers000000000002",
                    "path": "/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14",
                    "Title": "Vertr\xc3\xa4gsentwurf",
                }
            ]
        },
        "facet_counts": {
            "portal_type": {
                "opengever.dossier.businesscasedossier": {'count': 2},
                "opengever.document.document": {'count': 1}
            }
        },
        "highlighting": {
            "createtreatydossiers000000000001": {},
            "createexpireddossier000000000001": {},
            "createtreatydossiers000000000002": {
                "SearchableText": ["<em>Vertragsentwurf</em>"]
            }
        }
    }

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
    def test_simple_search_query(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?q=Kurz'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            self.solr.search.call_args[1]['query'],
            u'{!boost b=recip(ms(NOW,modified),3.858e-10,10,1)}'
            u'Title:Kurz^100 OR Title:Kurz*^20 OR SearchableText:Kurz^5 OR '
            u'SearchableText:Kurz* OR metadata:Kurz^10 OR metadata:Kurz*^2 '
            u'OR sequence_number_string:Kurz^2000')

    @browsing
    def test_raw_query(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?q.raw=Title:Kurz'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            self.solr.search.call_args[1]['query'],
            'Title:Kurz')

    @browsing
    def test_fallback_to_default_fields_if_fl_parameter_is_empty(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            self.solr.search.call_args[1]['fl'],
            'UID,Title,portal_type,path,review_state,Description')

    @browsing
    def test_blacklisted_attributes_are_skipped(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        # SearchableText is an unsupported field
        url = u'{}/@solrsearch?fl=SearchableText,allowedRolesAndUsers,getObject,UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            self.solr.search.call_args[1]['fl'],
            'path,UID,Title')

    @browsing
    def test_filter_queries(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = (u'{}/@solrsearch?fq=portal_type:opengever.document.document&'
               u'fq=path_parent:\\/plone\\/ordnungssystem\\/fuhrung'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            self.solr.search.call_args[1]['filters'],
            ['portal_type:opengever.document.document',
             'path_parent:\\/plone\\/ordnungssystem\\/fuhrung'])

    @browsing
    def test_returns_json_serialized_solr_docs(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            [{u'Title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
              u'UID': u'createtreatydossiers000000000001'},
             {u'Title': u'Abgeschlossene Vertr\xe4ge',
              u'UID': u'createexpireddossier000000000001'},
             {u'Title': u'Vertr\xe4gsentwurf',
              u'UID': u'createtreatydossiers000000000002'}],
            browser.json[u'items'])

    @browsing
    def test_returns_snippets(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title,snippets'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            [{u'Title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
              u'UID': u'createtreatydossiers000000000001',
              u'snippets': u''},
             {u'Title': u'Abgeschlossene Vertr\xe4ge',
              u'UID': u'createexpireddossier000000000001',
              u'snippets': u''},
             {u'Title': u'Vertr\xe4gsentwurf',
              u'UID': u'createtreatydossiers000000000002',
              u'snippets': u'<em>Vertragsentwurf</em>'}],
            browser.json[u'items'])

    @browsing
    def test_returns_facets(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn(u'facet_counts', browser.json)

    @browsing
    def test_default_start_and_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['start'], 0)
        self.assertEqual(self.solr.search.call_args[1]['rows'], 25)

    @browsing
    def test_custom_start_and_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title&start=20&rows=10'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['start'], 20)
        self.assertEqual(self.solr.search.call_args[1]['rows'], 10)

    @browsing
    def test_max_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title&start=0&rows=10000000'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['rows'], 1000)

    @browsing
    def test_default_sort(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?q=Foo&fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['sort'], 'score asc')

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['sort'], None)

    @browsing
    def test_custom_sort(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title&sort=modified asc'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['sort'], 'modified asc')
