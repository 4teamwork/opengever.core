from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestDocumentListing(IntegrationTestCase):

    @browsing
    def test_lists_documents(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-documents')
        self.maxDiff = None
        self.assertIn(
            {'': '',
             'Checked out by': '',
             'Delivery Date': '',
             'Document Author': '',
             'Document Date': '31.08.2016',
             'Public Trial': 'unchecked',
             'Receipt Date': '',
             'Reference Number': 'Client1 1.1 / 1 / 3',
             'Sequence Number': '3',
             'Subdossier': '',
             'Title': u'Vertr\xe4gsentwurf'},
            browser.css('.listing').first.dicts())
