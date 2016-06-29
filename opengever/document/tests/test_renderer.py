from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw import bumblebee
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document import renderer
from opengever.document.renderer import DocumentLinkRenderer
from opengever.testing import FunctionalTestCase


class TestDocumentLinkRenderer(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentLinkRenderer, self).setUp()
        self.converter_avaialable = renderer.PDFCONVERTER_AVAILABLE

    def tearDown(self):
        super(TestDocumentLinkRenderer, self).tearDown()
        renderer.PDFCONVERTER_AVAILABLE = self.converter_avaialable

    @browsing
    def test_is_prefixed_with_tooltiped_mimetype_icon(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkRenderer(document).render())

        tooltip_link = browser.css('a.tabbedview-tooltip')
        self.assertEquals([''], tooltip_link.text)
        self.assertEquals('tabbedview-tooltip icon-doc',
                          tooltip_link.first.get('class'))

    @browsing
    def test_is_linked_to_the_object(self, browser):
        document = create(Builder('document')
                          .titled('Anfrage Meier')
                          .with_dummy_content())

        browser.open_html(DocumentLinkRenderer(document).render())

        link = browser.css('a')[1]
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

        browser.open_html(DocumentLinkRenderer(document).render())
        self.assertEquals(
            'Ordnungssystem > 1. Ablage 1 > Hans Meier > Anfrage Meier',
            browser.css('.tooltip-breadcrumb').first.text)

    @browsing
    def test_tooltip_actions(self, browser):
        renderer.PDFCONVERTER_AVAILABLE = True
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkRenderer(document).render())
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

        browser.open_html(DocumentLinkRenderer(document_a).render())
        self.assertEquals([], browser.css('.removed_document'))

        browser.open_html(DocumentLinkRenderer(document_b).render())
        self.assertEquals(1, len(browser.css('.removed_document')))

    @browsing
    def test_preview_link_is_only_available_for_documents(self, browser):
        renderer.PDFCONVERTER_AVAILABLE = True
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.open_html(DocumentLinkRenderer(document).render())
        self.assertIn('PDF Preview', browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkRenderer(mail).render())
        self.assertNotIn('PDF Preview', browser.css('.tooltip-links a').text)

    @browsing
    def test_preview_link_is_only_available_when_pdfconverter_is_active(self, browser):
        document = create(Builder('document').with_dummy_content())

        renderer.PDFCONVERTER_AVAILABLE = True
        browser.open_html(DocumentLinkRenderer(document).render())
        self.assertIn('PDF Preview', browser.css('.tooltip-links a').text)

        renderer.PDFCONVERTER_AVAILABLE = False
        browser.open_html(DocumentLinkRenderer(document).render())
        self.assertNotIn('PDF Preview', browser.css('.tooltip-links a').text)

    @browsing
    def test_edit_metadata_link_is_not_available_for_trashed_documents(self, browser):
        self.grant('Administrator')
        document_a = create(Builder('document').with_dummy_content())
        document_b = create(Builder('document').with_dummy_content().trashed())

        browser.open_html(DocumentLinkRenderer(document_a).render())
        self.assertIn('Edit metadata', browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkRenderer(document_b).render())
        self.assertNotIn('Edit metadata', browser.css('.tooltip-links a').text)

    @browsing
    def test_checkout_link_is_only_available_for_documents(self, browser):
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.open_html(DocumentLinkRenderer(document).render())
        self.assertIn('Checkout and edit',
                      browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkRenderer(mail).render())
        self.assertNotIn('Checkout and edit',
                         browser.css('.tooltip-links a').text)

    @browsing
    def test_download_link_is_only_available_for_documents(self, browser):
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.open_html(DocumentLinkRenderer(document).render())
        self.assertIn('Download copy', browser.css('.tooltip-links a').text)

        browser.open_html(DocumentLinkRenderer(mail).render())
        self.assertNotIn('Download copy', browser.css('.tooltip-links a').text)


class TestDocumentLinkRendererWithActivatedBumblebee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_document_link_is_extend_with_showrom_data(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkRenderer(document).render())

        link = browser.css('.document_link')
        self.assertEquals('document_link showroom-item', link.get('class'))
        self.assertEquals(
            'http://nohost/plone/document-1/@@bumblebee-overlay-listing',
            link.get('data-showroom-target'))
        self.assertEquals(
            u'Testdokum\xc3\xa4nt',
            link.get('data-showroom-title'))

    @browsing
    def test_tooltip_contains_preview_thumbnail(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkRenderer(document).render())

        thumbnail_url = bumblebee.get_service_v3().get_representation_url(
            document, 'thumbnail')

        self.assertEquals(
            thumbnail_url, browser.css('.preview img').first.get('src'))
