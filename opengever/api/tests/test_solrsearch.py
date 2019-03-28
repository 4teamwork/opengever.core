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
                    "UID": "85bed8c49f6d4f8b841693c6a7c6cff1",
                    "Title": "My Folder 1",
                },
                {
                    "UID": "85a29144758f494c88df19182f749ed6",
                    "Title": "My Folder 2",
                },
                {
                    "UID": "9398dad21bcd49f8a197cd50d10ea778",
                    "Title": "My Document",
                }
            ]
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
    def test_passes_known_parameters_to_solr_utility(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?query=Title:Kurz*&fq=portal_type:opengever.document.document'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.solr.search.assert_called_once_with(
            fl='UID,Title,Description,path',
            filters='portal_type:opengever.document.document',
            query='Title:Kurz*')

    @browsing
    def test_fallback_to_default_fields_if_fl_parameter_is_empty(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.solr.search.assert_called_once_with(fl='UID,Title,Description,path')

    @browsing
    def test_not_supported_fields_are_skipped(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        # SearchableText is an unsupported field
        url = u'{}/@solrsearch?fl=UID,SearchableText,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.solr.search.assert_called_once_with(fl='UID,Title')

    @browsing
    def test_returns_json_serialized_solr_docs(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json=self.solr_search_response)

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            [{u'UID': u'85bed8c49f6d4f8b841693c6a7c6cff1',
              u'Title': u'My Folder 1'},
             {u'UID': u'85a29144758f494c88df19182f749ed6',
              u'Title': u'My Folder 2'},
             {u'UID': u'9398dad21bcd49f8a197cd50d10ea778',
              u'Title': u'My Document'}],
            browser.json)
