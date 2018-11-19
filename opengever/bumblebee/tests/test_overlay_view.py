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
    def test_bumblebee_overlay_does_not_render_empty_comment(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='bumblebee-overlay-listing')
        self.assertNotIn('Checkin comment:', browser.css('.metadata .title').text)

    @browsing
    def test_bumblebee_overlay_renders_comment(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, version_id=0)
        browser.open(self.document, view='bumblebee-overlay-listing')
        self.assertIn('Checkin comment: This is Version 0', browser.css('.metadata tr').text)

    @browsing
    def test_bumblebee_overlay_renders_comments_correctly_on_versioned_documents(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, version_id=0)
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        browser.open(
            self.document.absolute_url() + '/@checkin',
            method='POST',
            headers={'Accept': 'application/json'},
            )
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        browser.open(
            self.document.absolute_url() + '/@checkin',
            data='{"comment": "Foo bar."}',
            method='POST',
            headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
            )
        browser.open(self.document, view='bumblebee-overlay-document?version_id=0')
        self.assertIn('Checkin comment: This is Version 0', browser.css('.metadata tr').text)
        browser.open(self.document, view='bumblebee-overlay-document?version_id=1')
        self.assertNotIn('Checkin comment:', browser.css('.metadata .title').text)
        browser.open(self.document, view='bumblebee-overlay-document?version_id=2')
        self.assertIn('Checkin comment: Foo bar.', browser.css('.metadata tr').text)

    @browsing
    def test_render_download_link(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')
        download_link = browser.css('#action-download')[0].get('href')

        self.assertNotIn(
            'version_id',
            download_link,
            )

        create_document_version(self.document, version_id=0)

        browser.open(self.document, view='bumblebee-overlay-listing')
        download_link = browser.css('#action-download')[0].get('href')

        self.assertNotIn(
            'version_id',
            download_link,
            )

        browser.open(
            self.document,
            view='bumblebee-overlay-listing?version_id=0',
            )
        download_link = browser.css('#action-download')[0].get('href')

        self.assertNotIn(
            'version_id',
            download_link,
            )

        create_document_version(self.document, version_id=1)

        browser.open(self.document, view='bumblebee-overlay-listing')
        download_link = browser.css('#action-download')[0].get('href')

        self.assertNotIn(
            'version_id',
            download_link,
            )

        browser.open(
            self.document,
            view='bumblebee-overlay-listing?version_id=0',
            )
        download_link = browser.css('#action-download')[0].get('href')

        self.assertIn(
            'version_id=0',
            download_link,
            )

        browser.open(
            self.document,
            view='bumblebee-overlay-listing?version_id=1',
            )
        download_link = browser.css('#action-download')[0].get('href')

        self.assertNotIn(
            'version_id',
            download_link,
            )

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
                'Attach to email',
                'Open as PDF',
                'Open detail view',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_without_file(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.empty_document, view='bumblebee-overlay-listing')

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
                'Edit',
                'Checkin without comment',
                'Checkin with comment',
                'Cancel checkout',
                'Download copy',
                'Attach to email',
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

        browser.open(self.mail_eml, view='bumblebee-overlay-listing')

        self.assertEqual(
            [
                'Edit metadata',
                'Download copy',
                'Attach to email',
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
                'Attach to email',
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
                'Attach to email',
                'Open as PDF',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_actions_without_file(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.empty_document, view="bumblebee-overlay-document")

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
                'Edit',
                'Checkin without comment',
                'Checkin with comment',
                'Cancel checkout',
                'Download copy',
                'Attach to email',
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

        browser.open(self.mail_eml, view="bumblebee-overlay-document")

        self.assertEqual(
            [
                'Edit metadata',
                'Download copy',
                'Attach to email',
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
                'Attach to email',
                'Revert document',
                ],
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_description_is_intelligently_formatted(self, browser):
        self.login(self.regular_user, browser)
        self.document.description = u'\n\n Foo\n    Bar\n'
        browser.open(self.document, view="bumblebee-overlay-document")
        # Somehow what is `&nbsp;` in a browser is `\xa0` in ftw.testbrowser
        self.assertEqual(
            u'<br><br>\xa0Foo<br>\xa0\xa0\xa0\xa0Bar<br>',
            browser.css('.value.description div')[0].innerHTML,
        )

    @browsing
    def test_description_is_intelligently_formatted_on_mail(self, browser):
        self.login(self.regular_user, browser)
        self.mail_eml.description = u'\n\n Foo\n    Bar\n'
        browser.open(self.mail_eml, view="bumblebee-overlay-document")
        # Somehow what is `&nbsp;` in a browser is `\xa0` in ftw.testbrowser
        self.assertEqual(
            u'<br><br>\xa0Foo<br>\xa0\xa0\xa0\xa0Bar<br>',
            browser.css('.value.description div')[0].innerHTML,
        )


class TestBumblebeeOverlayViewsWithoutBumblebeeFeature(IntegrationTestCase):
    """Test we can disable Bumblebee."""

    @browsing
    def test_calling_view_raise_404_if_feature_is_deactivated(self, browser):
        view = BumblebeeOverlayBaseView(None, self.request)

        with self.assertRaises(NotFound):
            view()
