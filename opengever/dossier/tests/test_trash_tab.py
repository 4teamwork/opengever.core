from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestTrashTab(FunctionalTestCase):

    @browsing
    def test_trashed_documents_in_listing_are_linked(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('document')
               .within(dossier)
               .trashed())

        browser.login().visit(dossier, view='tabbedview_view-trash')

        items = browser.css('table.listing a.icon-document_empty')
        self.assertEqual(1, len(items))
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1',
            items.first.get('href'))
