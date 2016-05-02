from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from zExceptions import NotFound
import transaction


class TestBumblebeeOverlayWithoutBumblebeeFeature(FunctionalTestCase):

    @browsing
    def test_calling_mixin_raise_404_if_feature_is_deactivated(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        view = document.restrictedTraverse('bumblebee-overlay')

        with self.assertRaises(NotFound):
            view()


class TestGetPreviewPdfUrl(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_preview_pdf_url_as_string(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIn('preserved_as_paper.png', view.get_preview_pdf_url())
        transaction.commit()


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

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertEqual('example.docx', view.get_file_title())

    def test_returns_none_if_no_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIsNone(view.get_file_title())


class TestGetFileSize(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_file_size_if_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertEqual(26, view.get_file_size())

    def test_returns_none_if_no_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIsNone(view.get_file_size())


class TestGetCreator(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_link_to_creator(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIn('Test User (test_user_1_)', view.get_creator())


class TestGetDocumentDate(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_localized_document_date(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=date(2014, 1, 1)))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertEqual(u'Jan 01, 2014 01:00 AM', view.get_document_date())

    def test_returns_none_if_no_document_date_is_set(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=''))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIsNone(view.get_document_date())


class TestGetContainingDossier(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_the_containing_dossier(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=date(2014, 1, 1)))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertEqual(dossier, view.get_containing_dossier())


class TestGetSequenceNumber(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_sequense_number(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertEqual(1, view.get_sequence_number())


class TestGetReferenceNumber(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_reference_number(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertEqual('Client1 / 1 / 1', view.get_reference_number())


class TestGetCheckoutLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_checkout_link_as_string(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIn(
            'http://nohost/plone/dossier-1/document-1/editing_document',
            view.get_checkout_link())

    def test_returns_none_if_no_document_is_available_to_checkout(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIsNone(None, view.get_checkout_link())

    def test_returns_none_if_user_is_not_allowed_to_edit(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        view = document.restrictedTraverse('bumblebee-overlay')

        self.assertIn(
            'http://nohost/plone/dossier-1/document-1/editing_document',
            view.get_checkout_link())

        self.portal.acl_users.userFolderAddUser(
            'bond', 'secret', ['Member', 'Reader'], [])
        transaction.commit()

        login(self.portal, 'bond')

        view = document.restrictedTraverse('bumblebee-overlay')
        self.assertIsNone(None, view.get_checkout_link())


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

        view = document.restrictedTraverse('bumblebee-overlay')

        browser.open_html(view.get_download_copy_link())

        self.assertEqual('Download copy', browser.css('a').first.text)

    def test_returns_none_if_no_document_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')
        self.assertIsNone(view.get_download_copy_link())


class TestGetEditMetadataLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_edit_link_as_string(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/edit',
            view.get_edit_metadata_link())

    def test_returns_none_if_user_is_not_allowed_to_edit(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        view = document.restrictedTraverse('bumblebee-overlay')
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/edit',
            view.get_edit_metadata_link())

        self.portal.acl_users.userFolderAddUser(
            'bond', 'secret', ['Member', 'Reader'], [])
        transaction.commit()

        login(self.portal, 'bond')

        view = document.restrictedTraverse('bumblebee-overlay')
        self.assertIsNone(view.get_edit_metadata_link())
