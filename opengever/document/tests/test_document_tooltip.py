from datetime import datetime
from ftw import bumblebee
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.base import pdfconverter
from opengever.testing import FunctionalTestCase


class TestDocumentTooltip(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentTooltip, self).setUp()
        self.converter_avaialable = pdfconverter.PDFCONVERTER_AVAILABLE

    def tearDown(self):
        super(TestDocumentTooltip, self).tearDown()
        pdfconverter.PDFCONVERTER_AVAILABLE = self.converter_avaialable

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

        browser.login().open(document, view='tooltip')
        self.assertEquals(
            ['Ordnungssystem', '1. Ablage 1', 'Hans Meier', 'Anfrage Meier'],
            browser.css('.tooltip-breadcrumb li').text)

    @browsing
    def test_tooltip_actions(self, browser):
        pdfconverter.PDFCONVERTER_AVAILABLE = True
        document = create(Builder('document').with_dummy_content())

        browser.login().open(document, view='tooltip')
        preview, metadata, checkout, download = browser.css('.file-actions a')

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
    def test_preview_link_is_only_available_for_documents(self, browser):
        pdfconverter.PDFCONVERTER_AVAILABLE = True
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.login().open(document, view='tooltip')
        self.assertIn('PDF Preview', browser.css('.file-actions a').text)

        browser.open(mail, view='tooltip')
        self.assertNotIn('PDF Preview', browser.css('.file-actions a').text)

    @browsing
    def test_preview_link_is_only_available_when_pdfconverter_is_active(self, browser):
        document = create(Builder('document').with_dummy_content())

        pdfconverter.PDFCONVERTER_AVAILABLE = True
        browser.login().open(document, view='tooltip')
        self.assertIn('PDF Preview', browser.css('.file-actions a').text)

        pdfconverter.PDFCONVERTER_AVAILABLE = False
        browser.open(document, view='tooltip')
        self.assertNotIn('PDF Preview', browser.css('.file-actions a').text)

    @browsing
    def test_edit_metadata_link_is_not_available_for_trashed_documents(self, browser):
        self.grant('Administrator')
        document_a = create(Builder('document').with_dummy_content())
        document_b = create(Builder('document').with_dummy_content().trashed())

        browser.login().open(document_a, view='tooltip')
        self.assertIn('Edit metadata', browser.css('.file-actions a').text)

        browser.open(document_b, view='tooltip')
        self.assertNotIn('Edit metadata', browser.css('.file-actions a').text)

    @browsing
    def test_checkout_link_is_only_available_for_documents(self, browser):
        document = create(Builder('document').with_dummy_content())
        mail = create(Builder('mail'))

        browser.login().open(document, view='tooltip')
        self.assertIn('Checkout and edit',
                      browser.css('.file-actions a').text)

        browser.open(mail, view='tooltip')
        self.assertNotIn('Checkout and edit',
                         browser.css('.file-actions a').text)

    @browsing
    def test_download_link_is_available_for_documents_and_mails_when_file_exists(self, browser):
        document = create(Builder('document').with_dummy_content())
        document_without_file = create(Builder('document'))
        mail = create(Builder('mail').with_dummy_message())

        browser.login().open(document, view='tooltip')
        self.assertIn('Download copy', browser.css('.file-actions a').text)

        browser.login().open(mail, view='tooltip')
        self.assertIn('Download copy', browser.css('.file-actions a').text)

        browser.login().open(document_without_file, view='tooltip')
        self.assertNotIn('Download copy', browser.css('.file-actions a').text)


class TestDocumentLinkWidgetWithActivatedBumblebee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_tooltip_contains_preview_thumbnail(self, browser):
        with freeze(datetime(2016, 1, 1)):
            document = create(Builder('document').with_dummy_content())

            self.request.form['bid'] = 'THEBID'
            browser.login().open(document, {'bid': 'THEBID'}, view='tooltip')
            thumbnail_url = bumblebee.get_service_v3().get_representation_url(
                document, 'thumbnail')

            self.assertEquals(
                thumbnail_url,
                browser.css('.preview img').first.get('src'))
