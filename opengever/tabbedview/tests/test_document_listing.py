from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from Products.CMFPlone.utils import safe_unicode


class TestDocumentListing(IntegrationTestCase):

    @browsing
    def test_lists_documents(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')
        self.maxDiff = None

        expected_metadata = {
            '': '',
            'Checked out by': '',
            'Delivery Date': '03.01.2010',
            'Document Author': 'test_user_1_',
            'Document Date': '03.01.2010',
            'File extension': '.docx',
            'Public Trial': 'unchecked',
            'Receipt Date': '03.01.2010',
            'Reference Number': 'Client1 1.1 / 1 / 14',
            'Sequence Number': '14',
            'Subdossier': '',
            'Title': u'Vertr\xe4gsentwurf',
            'Creation Date': '31.08.2016',
            'Modification Date': '31.08.2016',
            'Keywords': 'Wichtig',
            }

        listings = browser.css('.listing').first.dicts()
        self.assertIn(expected_metadata, listings)

    def solr_response(self, *facets):
        solr_facets = []
        for facet in facets:
            solr_facets.extend([safe_unicode(facet), 1])

        return {u'facet_counts': {u'facet_fields': {u'Subject': solr_facets}}}

    @browsing
    def test_document_keywords_are_links(self, browser):
        self.activate_feature('solr')
        self.login(self.regular_user, browser=browser)

        self.mock_solr(response_json=self.solr_response('Wichtig'))

        browser.visit(self.dossier, view='tabbedview_view-documents', data={'subjects': ["Wichtig"]})
        table = browser.css('.listing').first

        # We isolate the keyword cell for self.document
        col_index = table.titles.index('Keywords')
        row_index = table.column("Title").index(self.document.title)
        keywords_cell = table.rows[row_index].cells[col_index]

        self.assertEqual("Wichtig", keywords_cell.text)
        links = keywords_cell.css("a")
        self.assertEqual(1, len(links))
        self.assertEqual('http://nohost/plone/@@search?Subject=Wichtig',
                         links.first.get("href"))

    @browsing
    def test_filter_documents_by_subjects(self, browser):
        self.activate_feature('solr')
        self.login(self.regular_user, browser=browser)

        self.mock_solr(response_json=self.solr_response('Wichtig', 'Subkeyword'))

        browser.visit(self.dossier, view='tabbedview_view-documents')
        table = browser.css('.listing').first
        self.assertLess(3, len(table.rows))

        # self.document and self.subdocument have the 'Wichtig' keyword
        browser.visit(self.dossier, view='tabbedview_view-documents', data={'subjects': ["Wichtig"]})
        table = browser.css('.listing').first
        self.assertEqual(3, len(table.rows))
        self.assertEqual(['Title', self.document.title, self.subdocument.title],
                         table.column("Title"))

        # self.subdocument and self.empty_document have the 'Subkeyword' keyword
        browser.visit(self.dossier, view='tabbedview_view-documents', data={'subjects': ["Subkeyword"]})
        table = browser.css('.listing').first
        self.assertEqual(3, len(table.rows))
        self.assertEqual(['Title', self.subdocument.title, self.empty_document.title],
                         table.column("Title"))

        # self.subdocument has both the 'Wichtig' and the 'Subkeyword' keyword
        browser.visit(self.dossier, view='tabbedview_view-documents', data={'subjects': ["Wichtig++Subkeyword"]})
        table = browser.css('.listing').first
        self.assertEqual(2, len(table.rows))
        self.assertEqual(['Title', self.subdocument.title],
                         table.column("Title"))
