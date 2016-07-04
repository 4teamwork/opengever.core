from ftw import bumblebee
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document.widgets import document_link
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.testing import FunctionalTestCase


class TestDocumentLinkWidget(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentLinkWidget, self).setUp()
        self.converter_avaialable = document_link.PDFCONVERTER_AVAILABLE

    def tearDown(self):
        super(TestDocumentLinkWidget, self).tearDown()
        document_link.PDFCONVERTER_AVAILABLE = self.converter_avaialable

    @browsing
    def test_link_contains_mimetype_icon_clas(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())

        link = browser.css('a.document_link').first
        self.assertEquals('tabbedview-tooltip document_link icon-doc',
                          link.get('class'))

    @browsing
    def test_is_linked_to_the_object(self, browser):
        document = create(Builder('document')
                          .titled('Anfrage Meier')
                          .with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())

        link = browser.css('a.document_link').first
        self.assertEquals('Anfrage Meier', link.text)
        self.assertEquals(document.absolute_url(), link.get('href'))

    @browsing
    def test_tooltip_contains_breadcrumb(self, browser):
        root = create(Builder('repository_root').titled(u'Ordnungssystem'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Ablage 1'))
        dossier = create(Builder('dossier')
                         .within(repo)
                         .titled('Hans Meier'.decode('utf-8')))
        document = create(Builder('document')
                          .titled('Anfrage Meier')
                          .within(dossier)
                          .with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())
        self.assertEquals(
            'Ordnungssystem > 1. Ablage 1 > Hans Meier > Anfrage Meier',
            browser.css('.tooltip-breadcrumb').first.text)

    @browsing
    def test_tooltip_actions(self, browser):
        document_link.PDFCONVERTER_AVAILABLE = True
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())
        preview, metadata, checkout, download = browser.css('.tooltip-links a')

        # preview
        self.assertEquals('PDF Preview', preview.text)
        self.assertEquals(
            'http://nohost/plone/document-1/@@download_pdfpreview',
            preview.get('href'))

        # metadata
        self.assertEquals('Edit metadata', metadata.text)
        self.assertEquals(
            'http://nohost/plone/document-1/edit_checker',
            metadata.get('href'))

        # checkout and edit
        self.assertEquals('Checkout and edit', checkout.text)
        self.assertTrue(checkout.get('href').startswith(
            'http://nohost/plone/document-1/editing_document?_authenticator='))

        # download copy
        self.assertEquals('Download copy', download.text)
        self.assertEquals(
            'http://nohost/plone/document-1/file_download_confirmation',
            download.get('href'))

    @browsing
    def test_removed_documents_are_prefixed_with_removed_marker(self, browser):
        document_a = create(Builder('document').with_dummy_content())
        document_b = create(Builder('document').with_dummy_content().removed())

        browser.open_html(DocumentLinkWidget(document_a).render())
        self.assertEquals([], browser.css('.removed_document'))

        browser.open_html(DocumentLinkWidget(document_b).render())
        self.assertEquals(1, len(browser.css('.removed_document')))

    @browsing
    def test_preview_link_is_only_available_for_documents(self, browser):
        document_link.PDFCONVERTER_AVAILABLE = True
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.open_html(DocumentLinkWidget(document).render())
        self.assertIn('PDF Preview', browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkWidget(mail).render())
        self.assertNotIn('PDF Preview', browser.css('.tooltip-links a').text)

    @browsing
    def test_preview_link_is_only_available_when_pdfconverter_is_active(self, browser):
        document = create(Builder('document').with_dummy_content())

        document_link.PDFCONVERTER_AVAILABLE = True
        browser.open_html(DocumentLinkWidget(document).render())
        self.assertIn('PDF Preview', browser.css('.tooltip-links a').text)

        document_link.PDFCONVERTER_AVAILABLE = False
        browser.open_html(DocumentLinkWidget(document).render())
        self.assertNotIn('PDF Preview', browser.css('.tooltip-links a').text)

    @browsing
    def test_edit_metadata_link_is_not_available_for_trashed_documents(self, browser):
        self.grant('Administrator')
        document_a = create(Builder('document').with_dummy_content())
        document_b = create(Builder('document').with_dummy_content().trashed())

        browser.open_html(DocumentLinkWidget(document_a).render())
        self.assertIn('Edit metadata', browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkWidget(document_b).render())
        self.assertNotIn('Edit metadata', browser.css('.tooltip-links a').text)

    @browsing
    def test_checkout_link_is_only_available_for_documents(self, browser):
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.open_html(DocumentLinkWidget(document).render())
        self.assertIn('Checkout and edit',
                      browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkWidget(mail).render())
        self.assertNotIn('Checkout and edit',
                         browser.css('.tooltip-links a').text)

    @browsing
    def test_download_link_is_only_available_for_documents(self, browser):
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.open_html(DocumentLinkWidget(document).render())
        self.assertIn('Download copy', browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkWidget(mail).render())
        self.assertNotIn('Download copy', browser.css('.tooltip-links a').text)


class TestDocumentLinkWidgetWithActivatedBumblebee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_document_link_is_extended_with_showrom_data(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())

        link = browser.css('a.document_link').first
        self.assertIn('showroom-item', link.get('class'))
        self.assertEquals(
            'http://nohost/plone/document-1/@@bumblebee-overlay-listing',
            link.get('data-showroom-target'))
        self.assertEquals(
            u'Testdokum\xe4nt',
            link.get('data-showroom-title'))

    @browsing
    def test_tooltip_contains_preview_thumbnail(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())

        thumbnail_url = bumblebee.get_service_v3().get_representation_url(
            document, 'thumbnail')

        self.assertEquals(
            thumbnail_url, browser.css('.preview img').first.get('src'))
