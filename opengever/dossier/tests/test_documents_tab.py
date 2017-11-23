from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestDocumentsTab(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentsTab, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))

        self.dossier = create(Builder('dossier'))
        self.subdossier = create(
            Builder('dossier')
            .within(self.dossier)
            .titled(u'S\xfcbdossier <Foo> Bar'))
        self.document = create(Builder('document').within(self.subdossier))

    @browsing
    def test_containing_subdossiers_are_linked(self, browser):
        browser.login().visit(self.dossier, view='tabbedview_view-documents')

        browser.css('table.listing').first.css('a.subdossierLink')
        link = browser.css('table.listing').first.css('a.subdossierLink').first
        # Title should be HTML escaped and encoded properly
        self.assertEqual(u'S\xfcbdossier &lt;Foo&gt; Bar', link.innerHTML)

        link.click()
        self.assertEqual(browser.url, self.subdossier.absolute_url())

    @browsing
    def test_documents_in_listing_are_linked(self, browser):
        browser.login().visit(self.dossier, view='tabbedview_view-documents')

        items = browser.css('table.listing a.icon-document_empty')
        self.assertEqual(1, len(items))
        self.assertEqual(
            'http://nohost/plone/dossier-1/dossier-2/document-1',
            items.first.get('href'))
