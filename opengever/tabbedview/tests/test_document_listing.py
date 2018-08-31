from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


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
            'Public Trial': 'unchecked',
            'Receipt Date': '03.01.2010',
            'Reference Number': 'Client1 1.1 / 1 / 12',
            'Sequence Number': '12',
            'Subdossier': '',
            'Title': u'Vertr\xe4gsentwurf',
            'Creation Date': '31.08.2016',
            'Modification Date': '31.08.2016',
            }

        listings = browser.css('.listing').first.dicts()

        self.assertIn(expected_metadata, listings)
