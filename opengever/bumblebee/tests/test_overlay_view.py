from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testbrowser import browsing
from opengever.bumblebee.browser.overlay import BumblebeeOverlayBaseView
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import create_document_version
from plone import api
from zExceptions import NotFound
import transaction


class TestBumblebeeOverlayListing(FunctionalTestCase):
    """Test Bumblebee in overlay listings."""

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_render_bumblebee_overlay_listing(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(1, len(browser.css('#file-preview')))

    @browsing
    def test_open_pdf_in_a_new_window_disabled(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertNotIn(
            'target=', browser.css('.function-pdf-preview').first.outerHTML)

    @browsing
    def test_open_pdf_in_a_new_window_enabled(self, browser):
        api.portal.set_registry_record('open_pdf_in_a_new_window',
                                       True,
                                       interface=IGeverBumblebeeSettings)

        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        browser.login().visit(document, view='bumblebee-overlay-listing')

        self.assertIn(
            'target=', browser.css('.function-pdf-preview').first.outerHTML)

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
            ['Edit metadata',
             'Checkout and edit',
             'Download copy',
             'Open as PDF',
             'Open detail view'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_without_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Edit metadata', 'Open detail view'],
            browser.css('.file-action-buttons a').text)

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
            ['Edit metadata',
             'Checkout and edit',
             'Checkin without comment',
             'Checkin with comment',
             'Download copy',
             'Open as PDF',
             'Open detail view'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_with_file_checked_out_by_another_user(self, browser):
        create(Builder('user')
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
            ['Open as PDF',
             'Open detail view'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_with_mail(self, browser):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail')
                      .with_dummy_message()
                      .within(dossier))

        browser.login().visit(mail, view="bumblebee-overlay-listing")

        self.assertEqual(
            ['Edit metadata',
             'Download copy',
             'Open as PDF',
             'Open detail view'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_with_versioned_document(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        create_document_version(document, version_id=1)
        transaction.commit()

        browser.login()
        browser.open(document, view="bumblebee-overlay-document?version_id=1")

        self.assertEqual(
            ['Download copy', 'Revert document'],
            browser.css('.file-action-buttons a').text)


class TestBumblebeeOverlayDocument(FunctionalTestCase):
    """Test Bumblebee on document overlays."""

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_render_bumblebee_overlay_document(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(1, len(browser.css('#file-preview')))

    @browsing
    def test_title_is_linked_to_document_view(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .titled(u"Anfrage Meier")
                          .within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-document")

        title = browser.css('.sidebar > header .title').first
        self.assertEqual("Anfrage Meier", title.text)
        self.assertEqual(document.absolute_url(), title.get("href"))

    @browsing
    def test_dossier_title_is_linked_to_the_dossier(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier A'))
        document = create(Builder('document')
                          .titled(u"Anfrage Meier")
                          .within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-document")

        dossier_link = browser.css('.metadata .value a')[1]
        self.assertEqual('Dossier A', dossier_link.text)
        self.assertEqual(dossier.absolute_url(), dossier_link.get('href'))

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
            ['Edit metadata',
             'Checkout and edit',
             'Download copy',
             'Open as PDF'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_without_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Edit metadata'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_with_checked_out_file(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out())

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Edit metadata',
             'Checkout and edit',
             'Checkin without comment',
             'Checkin with comment',
             'Download copy',
             'Open as PDF'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_with_file_checked_out_by_another_user(self, browser):
        create(Builder('user')
               .with_userid('hans')
               .with_roles('Contributor', 'Editor', 'Reader'))
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out_by('hans'))

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Open as PDF'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_with_mail(self, browser):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail')
                      .with_dummy_message()
                      .within(dossier))

        browser.login().visit(mail, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Edit metadata',
             'Download copy',
             'Open as PDF'],
            browser.css('.file-action-buttons a').text)

    @browsing
    def test_actions_with_versioned_document(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        create_document_version(document, version_id=1)
        transaction.commit()

        browser.login()
        browser.open(document, view="bumblebee-overlay-document?version_id=1")

        self.assertEqual(
            ['Download copy',
             'Revert document'],
            browser.css('.file-action-buttons a').text)


class TestBumblebeeOverlayViewsWithoutBumblebeeFeature(FunctionalTestCase):
    """Test we can disable Bumblebee."""

    @browsing
    def test_calling_view_raise_404_if_feature_is_deactivated(self, browser):
        view = BumblebeeOverlayBaseView(None, self.request)

        with self.assertRaises(NotFound):
            view()
