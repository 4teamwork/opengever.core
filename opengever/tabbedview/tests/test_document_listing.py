from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestDocumentListing(IntegrationTestCase):

    @browsing
    def test_lists_documents(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')
        self.maxDiff = None

        listings = browser.css('.listing').first.dicts()

        self.assertIn(
            {'': '',
             'Checked out by': '',
             'Delivery Date': '03.01.2010',
             'Document Author': 'test_user_1_',
             'Document Date': '03.01.2010',
             'Public Trial': 'unchecked',
             'Receipt Date': '03.01.2010',
             'Reference Number': 'Client1 1.1 / 1 / 4',
             'Sequence Number': '4',
             'Subdossier': '',
             'Title': u'Vertr\xe4gsentwurf'},
            listings)
