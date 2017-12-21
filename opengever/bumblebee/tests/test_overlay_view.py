from ftw.testbrowser import browsing
from opengever.bumblebee.browser.overlay import BumblebeeOverlayBaseView
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import create_document_version
from zExceptions import NotFound
from zope.component import getMultiAdapter


class TestBumblebeeOverlayListing(IntegrationTestCase):
    """Test Bumblebee in overlay listings."""

    features = (
        'bumblebee',
        )

    @browsing
    def test_render_bumblebee_overlay_listing(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')
        self.assertEqual(1, len(browser.css('#file-preview')))

    @browsing
    def test_open_pdf_in_a_new_window_disabled(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertNotIn(
            'target=',
            browser.css('.function-pdf-preview').first.outerHTML,
            )

    @browsing
    def test_open_pdf_in_a_new_window_enabled(self, browser):
        self.activate_feature('bumblebee-open-pdf-new-tab')
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertIn(
            'target=',
            browser.css('.function-pdf-preview').first.outerHTML,
            )

    @browsing
    def test_actions_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(
            [
                'Edit metadata',
                'Checkout and edit',
                'Download copy',
                'Open as PDF',
                'Open detail view',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(
            [
                'Edit metadata',
                'Open detail view',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_checked_out_file(self, browser):
        self.login(self.regular_user, browser)
        getMultiAdapter(
            (self.document, self.request),
            ICheckinCheckoutManager,
            ).checkout()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(
            [
                'Edit metadata',
                'Checkout and edit',
                'Checkin without comment',
                'Checkin with comment',
                'Download copy',
                'Open as PDF',
                'Open detail view',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_file_checked_out_by_another_user(self, browser):
        self.login(self.dossier_responsible, browser)
        getMultiAdapter(
            (self.document, self.request),
            ICheckinCheckoutManager,
            ).checkout()
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(
            [
                'Open as PDF',
                'Open detail view',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_mail(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.mail, view='bumblebee-overlay-listing')

        self.assertEqual(
            [
                'Edit metadata',
                'Download copy',
                'Open as PDF',
                'Open detail view',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_versioned_document(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, version_id=0)

        browser.open(
            self.document,
            view='bumblebee-overlay-document?version_id=0',
            )

        self.assertEqual(
            [
                'Download copy',
                'Revert document',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_warning_only_rendered_on_old_version(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, version_id=0)

        browser.open(self.document, view='bumblebee-overlay-document')
        self.assertFalse(browser.css('.info-viewlets .portalMessage.warning'))

        browser.open(
            self.document,
            view='bumblebee-overlay-document?version_id=0',
            )
        self.assertFalse(browser.css('.info-viewlets .portalMessage.warning'))

        create_document_version(self.document, version_id=1)

        browser.open(self.document, view='bumblebee-overlay-document')
        self.assertFalse(browser.css('.info-viewlets .portalMessage.warning'))

        browser.open(
            self.document,
            view='bumblebee-overlay-document?version_id=1',
            )
        self.assertFalse(browser.css('.info-viewlets .portalMessage.warning'))

        browser.open(
            self.document,
            view='bumblebee-overlay-document?version_id=0',
            )
        self.assertTrue(browser.css('.info-viewlets .portalMessage.warning'))


class TestBumblebeeOverlayDocument(IntegrationTestCase):
    """Test Bumblebee on document overlays."""

    features = (
        'bumblebee',
        )

    @browsing
    def test_render_bumblebee_overlay_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view="bumblebee-overlay-document")

        self.assertEqual(1, len(browser.css('#file-preview')))

    @browsing
    def test_dossier_title_is_linked_to_the_dossier(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view="bumblebee-overlay-document")

        dossier_link = browser.css('.metadata .value a')[1]
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            dossier_link.text,
            )
        self.assertEqual(self.dossier.absolute_url(), dossier_link.get('href'))

    @browsing
    def test_actions_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view="bumblebee-overlay-document")

        self.assertEqual(
            [
                'Edit metadata',
                'Checkout and edit',
                'Download copy',
                'Open as PDF',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view="bumblebee-overlay-document")

        self.assertEqual(
            [
                'Edit metadata',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_checked_out_file(self, browser):
        self.login(self.regular_user, browser)
        getMultiAdapter(
            (self.document, self.request),
            ICheckinCheckoutManager,
            ).checkout()

        browser.open(self.document, view="bumblebee-overlay-document")

        self.assertEqual(
            [
                'Edit metadata',
                'Checkout and edit',
                'Checkin without comment',
                'Checkin with comment',
                'Download copy',
                'Open as PDF',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_file_checked_out_by_another_user(self, browser):
        self.login(self.dossier_responsible, browser)
        getMultiAdapter(
            (self.document, self.request),
            ICheckinCheckoutManager,
            ).checkout()
        self.login(self.regular_user, browser)

        browser.open(self.document, view="bumblebee-overlay-document")

        self.assertEqual(
            [
                'Open as PDF',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_mail(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.mail, view="bumblebee-overlay-document")

        self.assertEqual(
            [
                'Edit metadata',
                'Download copy',
                'Open as PDF',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_with_versioned_document(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, version_id=0)

        browser.open(
            self.document,
            view="bumblebee-overlay-document?version_id=0",
            )

        self.assertEqual(
            [
                'Download copy',
                'Revert document',
                ],
            browser.css('.file-action-buttons a').text,
            )


class TestBumblebeeOverlayViewsWithoutBumblebeeFeature(IntegrationTestCase):
    """Test we can disable Bumblebee."""

    @browsing
    def test_calling_view_raise_404_if_feature_is_deactivated(self, browser):
        view = BumblebeeOverlayBaseView(None, self.request)

        with self.assertRaises(NotFound):
            view()
