from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from zExceptions import NotFound
from opengever.bumblebee.browser.overlay import BumblebeeOverlayBaseView


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

    @browsing
    def test_actions_with_mail(self, browser):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail')
                      .with_dummy_message()
                      .within(dossier))

        browser.login().visit(mail, view="bumblebee-overlay-listing")

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

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Download copy',
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

        browser.login().visit(document, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Download copy',
             'Open as PDF',
             'Edit metadata'],
            browser.css('.file-actions a').text)

    @browsing
    def test_actions_with_mail(self, browser):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail')
                      .with_dummy_message()
                      .within(dossier))

        browser.login().visit(mail, view="bumblebee-overlay-document")

        self.assertEqual(
            ['Download copy',
             'Open as PDF',
             'Edit metadata'],
            browser.css('.file-actions a').text)


class TestBumblebeeOverlayViewsWithoutBumblebeeFeature(FunctionalTestCase):

    @browsing
    def test_calling_view_raise_404_if_feature_is_deactivated(self, browser):
        view = BumblebeeOverlayBaseView(None, self.request)

        with self.assertRaises(NotFound):
            view()
