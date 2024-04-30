from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase


class TestDocumentListing(SolrIntegrationTestCase):

    @browsing
    def test_lists_documents(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')
        self.maxDiff = None

        expected_metadata = {
            '': '',
            'Checked out by': '',
            'Sent date': '03.01.2010',
            'Author': 'test_user_1_',
            'Document date': '03.01.2010',
            'File extension': '.docx',
            'Disclosure status': 'not assessed',
            'Received date': '03.01.2010',
            'Reference number': 'Client1 1.1 / 1 / 14',
            'Sequence number': '14',
            'Subdossier': '',
            'Title': u'Vertr\xe4gsentwurf',
            'Creation date': '31.08.2016',
            'Modification date': '31.08.2016',
            'Keywords': 'Wichtig',
        }

        listings = browser.css('.listing').first.dicts()
        self.assertIn(expected_metadata, listings)

    @browsing
    def test_document_keywords_are_links(self, browser):
        self.login(self.regular_user, browser=browser)

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
        self.login(self.regular_user, browser=browser)

        browser.visit(self.dossier, view='tabbedview_view-documents')
        table = browser.css('.listing').first
        self.assertEqual(13, len(table.rows))

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

    @browsing
    def test_filters_is_available_on_the_no_content_page(self, browser):
        self.activate_feature('extjs')
        self.login(self.regular_user, browser=browser)

        browser.visit(self.dossier, view='tabbedview_view-documents',
                      data={'subjects': ["secret"]})

        self.assertEqual(
            [
                u'Subkeyword',
                u'Subkeyw\xf6rd',
                u'Subsubkeyword',
                u'Subsubkeyw\xf6rd',
                u'Wichtig',
            ],
            browser.css('select.keyword-widget option').text)

    @browsing
    def test_correctly_sorts_on_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {'sort': 'reference', 'dir': 'ASC'}
        browser.visit(self.leaf_repofolder, view='tabbedview_view-documents', data=data)

        data = browser.css('.listing').first.lists()
        fields = data.pop(0)
        refnum_index = fields.index('Reference number')
        refnums = [each[refnum_index] for each in data]

        self.assertEqual([
            'Client1 1.1 / 1 / 14',
            'Client1 1.1 / 1 / 15',
            'Client1 1.1 / 1 / 18',
            'Client1 1.1 / 1 / 19',
            'Client1 1.1 / 1 / 20',
            'Client1 1.1 / 1 / 29',
            'Client1 1.1 / 1 / 30',
            'Client1 1.1 / 1 / 33',
            'Client1 1.1 / 1 / 35',
            'Client1 1.1 / 1.1 / 22',
            'Client1 1.1 / 1.1 / 24',
            'Client1 1.1 / 1.1.1 / 23',
            'Client1 1.1 / 2 / 26',
            'Client1 1.1 / 3 / 27',
            'Client1 1.1 / 5.1 / 28',
            'Client1 1.1 / 6 / 31',
            'Client1 1.1 / 7 / 32',
            'Client1 1.1 / 7 / 34',
            'Client1 1.1 / 11 / 43',
            'Client1 1.1 / 12 / 44',
            'Client1 1.1 / 12 / 45',
        ], refnums)
