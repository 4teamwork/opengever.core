from ftw.testbrowser import browsing
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.testing import SolrIntegrationTestCase


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

    @browsing
    def test_document_listing_select_all(self, browser):
        self.login(self.regular_user, browser)

        # check amount of total items
        browser.open(
            self.branch_repofolder,
            view='tabbed_view/listing?view_name=documents-proxy&pagesize=10000'
        )
        self.assertEqual(21, len(browser.css('table.listing tbody tr')))

        # load page 2 with pagesize of 3
        browser.open(
            self.branch_repofolder,
            view='tabbed_view/select_all?view_name=documents-proxy&pagesize=3&pagenumber=2&selected_count=3'
        )
        # 3 before + 3 already loaded + 13 after = 19 total
        self.assertEqual(3, len(browser.css('#above_visibles input')))
        self.assertEqual(15, len(browser.css('#beneath_visibles input')))

    @browsing
    def test_document_listing_select_all_with_search(self, browser):
        self.login(self.regular_user, browser)

        # check amount of total items with text "vertrag"
        browser.open(
            self.branch_repofolder,
            view='tabbed_view/listing?view_name=documents-proxy&pagesize=10000&searchable_text=vertrag'
        )
        self.assertEqual(11, len(browser.css('table.listing tbody tr')))

        # load page 2 with pagesize of 3  with text "vertrag"
        browser.open(
            self.branch_repofolder,
            view='tabbed_view/select_all?view_name=documents-proxy&pagesize=3&pagenumber=2&selected_count=3&searchable_text=vertrag'
        )
        # 3 before + 3 already loaded + 5 after = 11 total
        self.assertEqual(3, len(browser.css('#above_visibles input')))
        self.assertEqual(5, len(browser.css('#beneath_visibles input')))
