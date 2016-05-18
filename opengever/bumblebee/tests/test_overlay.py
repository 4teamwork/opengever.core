from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testbrowser import browsing
from opengever.bumblebee.browser.overlay import BumblebeeOverlayMixin
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from zExceptions import NotFound


class MockOverlayView(BumblebeeOverlayMixin):

    def __init__(self, context, request):
        self.context = context
        self.request = request


class TestBumblebeeOverlayListing(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_render_bumblebee_overlay_listing(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(1, len(browser.css('#file-preview')))

    @browsing
    def test_actions_with_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Open detail view',
             'Download copy',
             'Open as PDF',
             'Edit metadata',
             'Checkout and edit'],
            browser.css('.file-actions a').text)

    @browsing
    def test_actions_without_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Open detail view', 'Edit metadata'],
            browser.css('.file-actions a').text)

    @browsing
    def test_actions_with_checked_out_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out())

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Open detail view',
             'Download copy',
             'Open as PDF',
             'Edit metadata',
             'Checkout and edit',
             'Checkin without comment',
             'Checkin with comment'],
            browser.css('.file-actions a').text)

    @browsing
    def test_actions_with_file_checked_out_by_another_user(self, browser):
        hans = create(Builder('user')
                      .with_userid('hans')
                      .with_roles('Contributor', 'Editor', 'Reader'))
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out_by('hans'))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Open detail view',
             'Download copy',
             'Open as PDF',
             'Edit metadata'],
            browser.css('.file-actions a').text)


class TestBumblebeeOverlayDocument(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_render_bumblebee_overlay_document(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(1, len(browser.css('#file-preview')))

    @browsing
    def test_actions_with_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Download copy',
             'Open as PDF',
             'Edit metadata',
             'Checkout and edit'],
            browser.css('.file-actions a').text)

    @browsing
    def test_actions_without_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Edit metadata'],
            browser.css('.file-actions a').text)

    @browsing
    def test_actions_with_checked_out_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out())

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Open detail view',
             'Download copy',
             'Open as PDF',
             'Edit metadata',
             'Checkout and edit',
             'Checkin without comment',
             'Checkin with comment'],
            browser.css('.file-actions a').text)

    @browsing
    def test_actions_with_file_checked_out_by_another_user(self, browser):
        hans = create(Builder('user')
                      .with_userid('hans')
                      .with_roles('Contributor', 'Editor', 'Reader'))
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out_by('hans'))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Open detail view',
             'Download copy',
             'Open as PDF',
             'Edit metadata'],
            browser.css('.file-actions a').text)


class TestBumblebeeOverlayWithoutBumblebeeFeature(FunctionalTestCase):

    @browsing
    def test_calling_mixin_raise_404_if_feature_is_deactivated(self, browser):
        view = MockOverlayView(None, self.request)

        with self.assertRaises(NotFound):
            view()


class TestGetPreviewPdfUrl(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_preview_pdf_url_as_string(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertIn('not_digitally_available.png', view.get_preview_pdf_url())


class TestGetOpenAsPdfLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_pdf_url_as_string(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())

        view = MockOverlayView(document, self.request)

        self.assertIn(
            '/YnVtYmxlYmVl/api/v3/resource/', view.get_open_as_pdf_link())

    def test_returns_none_if_no_mimetype_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertIsNone(view.get_open_as_pdf_link())

    def test_returns_none_if_mimetype_is_not_supported(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              "data", name=u"test.notsupported"))

        view = MockOverlayView(document, self.request)

        self.assertIsNone(view.get_open_as_pdf_link())


class TestGetPdfFilename(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_changes_filename_extension_to_pdf_and_returns_filename(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              "data", name=u"test.docx"))

        view = MockOverlayView(document, self.request)

        self.assertEqual('testdokumant.docx', document.file.filename)
        self.assertEqual('testdokumant.pdf', view.get_pdf_filename())

    def test_returns_none_if_no_file_is_given(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertIsNone(view.get_pdf_filename())


class TestGetFileTitle(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_file_title_if_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .titled('Example')
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        view = MockOverlayView(document, self.request)

        self.assertEqual('example.docx', view.get_file_title())

    def test_returns_none_if_no_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertIsNone(view.get_file_title())


class TestGetFileSize(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_file_size_in_kb_if_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        view = MockOverlayView(document, self.request)

        self.assertEqual(26, view.get_file_size())

    def test_returns_none_if_no_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertIsNone(view.get_file_size())


class TestGetCreator(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_link_to_creator(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)
        creator_link = view.get_creator_link()

        self.assertIn('Test User (test_user_1_)', creator_link)
        self.assertIn('http://nohost/plone/@@user-details/test_user_1_',
                      creator_link)


class TestGetDocumentDate(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_localized_document_date(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=date(2014, 1, 1)))

        view = MockOverlayView(document, self.request)

        self.assertEqual(u'Jan 01, 2014', view.get_document_date())

    def test_returns_none_if_no_document_date_is_set(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=''))

        view = MockOverlayView(document, self.request)

        self.assertIsNone(view.get_document_date())


class TestGetContainingDossier(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_the_containing_dossier(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=date(2014, 1, 1)))

        view = MockOverlayView(document, self.request)

        self.assertEqual(dossier, view.get_containing_dossier())


class TestGetSequenceNumber(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_sequence_number(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertEqual(1, view.get_sequence_number())


class TestGetReferenceNumber(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_reference_number(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertEqual('Client1 / 1 / 1', view.get_reference_number())


class TestGetCheckoutLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_checkout_and_edit_url(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        view = MockOverlayView(document, self.request)

        self.assertIn(
            'http://nohost/plone/dossier-1/document-1/editing_document',
            view.get_checkout_url())

    def test_returns_none_if_no_document_is_available_to_checkout(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)

        self.assertIsNone(None, view.get_checkout_url())

    def test_returns_none_if_user_is_not_allowed_to_edit(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))
        create(Builder('user')
               .with_userid('bond')
               .with_roles('Member', 'Reader'))

        view = MockOverlayView(document, self.request)

        self.assertIn(
            'http://nohost/plone/dossier-1/document-1/editing_document',
            view.get_checkout_url())

        login(self.portal, 'bond')
        self.assertIsNone(None, view.get_checkout_url())


class TestGetDownloadCopyLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_returns_download_copy_link_as_html_link(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        view = MockOverlayView(document, self.request)

        browser.open_html(view.get_download_copy_link())

        self.assertEqual('Download copy', browser.css('a').first.text)

    def test_returns_none_if_no_document_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)
        self.assertIsNone(view.get_download_copy_link())


class TestGetEditMetadataLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_edit_metadata_url(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = MockOverlayView(document, self.request)
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/edit',
            view.get_edit_metadata_url())

    def test_returns_none_if_user_is_not_allowed_to_edit(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        create(Builder('user')
               .with_userid('bond')
               .with_roles('Member', 'Reader'))

        view = MockOverlayView(document, self.request)

        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/edit',
            view.get_edit_metadata_url())

        login(self.portal, 'bond')
        self.assertIsNone(view.get_edit_metadata_url())
