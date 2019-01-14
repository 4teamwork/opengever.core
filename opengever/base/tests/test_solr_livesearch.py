from ftw.solr.interfaces import IFtwSolrLayer
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zope.interface import alsoProvides


class TestSolrLivesearchReply(IntegrationTestCase):

    features = ('solr', )

    def setUp(self):
        super(TestSolrLivesearchReply, self).setUp()
        alsoProvides(self.request, IFtwSolrLayer)
        self.livesearch = self.portal.unrestrictedTraverse('@@livesearch_reply')
        self.request.form.update({'q': 'foo'})
        self.solr_search_response = {
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
                        "Description": "",
                        "getIcon": "",
                        "id": "my-folder-1",
                        "path": "/my-folder-1",
                        "portal_type": "opengever.dossier.businesscasedossier"
                    },
                    {
                        "UID": "85a29144758f494c88df19182f749ed6",
                        "Title": "My Folder 2",
                        "Description": "",
                        "getIcon": "",
                        "path": "/my-folder-2",
                        "id": "my-folder-2",
                        "portal_type": "opengever.dossier.businesscasedossier",
                    },
                    {
                        "UID": "9398dad21bcd49f8a197cd50d10ea778",
                        "Title": "My Document",
                        "Description": "",
                        "getIcon": "icon_dokument_word.gif",
                        "path": "/my-folder-1/my-document",
                        "id": "my-document",
                        "portal_type": "opengever.document.document",
                    }
                        ]
                }
            }

    @browsing
    def test_testing_solr_livesearch(self, browser):
        """Make sure we are testing the solr livesearch reply"""
        self.solr = self.mock_solr(response_json=self.solr_search_response)
        browser.open_html(self.livesearch())
        self.assertIn("solr", browser.css(".livesearchContainer").first.classes)

    @browsing
    def test_livesearch_reply_listing(self, browser):
        self.solr = self.mock_solr(response_json=self.solr_search_response)
        browser.open_html(self.livesearch())

        link_nodes = browser.css('.dropdown-list-item')
        self.assertEqual(4, len(link_nodes))

        expected_titles = ['My Folder 1', 'My Folder 2',
                           'My Document', 'Advanced Search&#8230;']
        self.assertEqual(expected_titles, [node.text for node in link_nodes])

    @browsing
    def test_livesearch_reply_escapes_title(self, browser):
        self.solr_search_response["response"]["docs"][0]["Title"] = u"<script>alert('evil');</script>"
        self.solr = self.mock_solr(response_json=self.solr_search_response)
        browser.open_html(self.livesearch())

        link_node = browser.css('.dropdown-list-item').first
        # lxml unescapes attributes for us. we want to test that the title
        # has been escaped correctly and thus use browser.contents only.
        self.assertIn('title="&lt;script&gt;alert(\'evil\');&lt;/script&gt;"',
                      link_node.outerHTML)
        # also test title that is displayed
        self.assertIn('&lt;script&gt;alert(\'evil\');&lt;',
                      link_node.innerHTML)

    @browsing
    def test_livesearch_reply_show_more(self, browser):
        self.solr_search_response["response"]["numFound"] = 4
        self.request.form.update({'limit': '3'})
        self.solr = self.mock_solr(response_json=self.solr_search_response)
        browser.open_html(self.livesearch())

        link_nodes = browser.css('.dropdown-list-item')
        self.assertEqual(5, len(link_nodes))

        expected_titles = ['My Folder 1', 'My Folder 2', 'My Document',
                           'Advanced Search&#8230;', 'Show all items']
        self.assertEqual(expected_titles, [node.text for node in link_nodes])

        self.assertEqual('@@search?SearchableText=foo&path=/plone',
                         link_nodes[-1].get("href"))

    @browsing
    def test_livesearch_reply_empty_result(self, browser):
        self.solr_search_response["response"]["docs"] = []
        self.solr_search_response["response"]["numFound"] = 0
        self.solr = self.mock_solr(response_json=self.solr_search_response)
        browser.open_html(self.livesearch())

        link_nodes = browser.css('.dropdown-list-item')
        self.assertEqual(2, len(link_nodes))

        expected_titles = ['No matching results found.',
                           'Advanced Search&#8230;']
        self.assertEqual(expected_titles, [node.text for node in link_nodes])

        link_node = browser.css('.dropdown-list-item').first
        self.assertEqual('LSNothingFound', link_node.get("id"))
