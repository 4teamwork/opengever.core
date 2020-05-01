from ftw.testbrowser import browsing
from opengever.testing.integration_test_case import SolrIntegrationTestCase


class TestTrashTab(SolrIntegrationTestCase):

    @browsing
    def test_trashed_documents_in_listing_are_linked(self, browser):
        self.login(self.regular_user, browser)

        self.trash_documents(self.document)
        self.commit_solr()

        browser.visit(self.dossier, view='tabbedview_view-trash')
        items = browser.css('table.listing a.document_link')
        self.assertEqual(1, len(items))
        self.assertEqual(
            self.document.absolute_url(),
            items.first.get('href'))
