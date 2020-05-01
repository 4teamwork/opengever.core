from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase
from opengever.base.behaviors.base import IOpenGeverBase


class TestDocumentsTab(SolrIntegrationTestCase):

    @browsing
    def test_containing_subdossiers_are_linked(self, browser):
        self.login(self.regular_user, browser)
        IOpenGeverBase(self.subdossier).title = u'S\xfcbdossier <Foo> Bar'

        self.subdocument.reindexObject()
        self.commit_solr()

        browser.open(self.dossier, view='tabbedview_view-documents')
        link = browser.css('table.listing').first.css('a.subdossierLink')[-1]
        self.assertEqual(u'S\xfcbdossier &lt;Foo&gt; Bar', link.innerHTML)

        link.click()
        self.assertEqual(browser.url, self.subdossier.absolute_url())

    @browsing
    def test_documents_in_listing_are_linked(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='tabbedview_view-documents')
        items = browser.css('table.listing a.icon-xlsx')
        self.assertEqual(2, len(items))

        expected_url = (
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22'
        )
        self.assertEqual(expected_url, items.first.get('href'))
