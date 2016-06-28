from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase


class TestTrashTab(FunctionalTestCase):

    @browsing
    def test_trashed_documents_in_listing_are_linked(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('document')
               .within(dossier)
               .trashed())

        browser.login().visit(dossier, view='tabbedview_view-trash')

        items = browser.css('table.listing a.contenttype-opengever-document-document')
        self.assertEqual(1, len(items))
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1',
            items.first.get('href'))


class TestBumblebeeTrashTab(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_trashed_documents_in_listing_link_to_overlay(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('document')
               .within(dossier)
               .with_dummy_content()
               .trashed())

        browser.login().visit(dossier, view='tabbedview_view-trash')

        items = browser.css('table.listing a.showroom-item')
        self.assertEqual(1, len(items))
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/@@bumblebee-overlay-listing',
            items.first.get('data-showroom-target'))
