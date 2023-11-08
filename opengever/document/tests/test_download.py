from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
import transaction


class TestDocumentDownloadConfirmation(IntegrationTestCase):
    """Test the document download confirmation overlay."""

    @browsing
    def test_download_copy_with_overlay_creates_journal_entry(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version')
        versioner.create_version('Some updates.')
        browser.open(self.document, view='tabbed_view/listing', data={'view_name': 'overview'})
        browser.find('Download copy').click()
        browser.find('Download').click()
        self.assert_journal_entry(self.document, 'File copy downloaded', 'Document copy downloaded current version (1)')

    @browsing
    def test_download_copy_without_overlay_creates_journal_entry(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version.')
        DownloadConfirmationHelper(self.document).deactivate()
        browser.open(self.document, view='tabbed_view/listing', data={'view_name': 'overview'})
        browser.find('Download copy').click()
        self.assert_journal_entry(self.document, 'File copy downloaded', 'Document copy downloaded current version (0)')

    @browsing
    def test_disable_copy_download_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='tabbed_view/listing', data={'view_name': 'overview'})
        self.assertEquals(1, len(browser.css('.link-overlay')))
        browser.css('.function-download-copy.link-overlay').first.click()
        browser.fill({"disable_download_confirmation": "on"}).submit()
        self.assertEquals(0, len(browser.css('.link-overlay')))
        self.assertFalse('file_download_confirmation' in browser.contents)

    @browsing
    def test_download_confirmation_for_empty_file(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.empty_document, view='file_download_confirmation')
        self.assertEqual([u'Document L\xe4\xe4r has no file.'], warning_messages())

    @browsing
    def test_download_confirmation_view_for_download(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='file_download_confirmation')
        self.assertEqual(
            "You're downloading a copy of the document Vertraegsentwurf.docx",
            browser.css(".details > p").first.text,
        )
        browser.find('Download').click()
        self.assertEqual(
            "{}/download?error_as_message=1".format(self.document.absolute_url()),
            browser.url)
        self.assertEqual(self.document.file.data, browser.contents)

    @browsing
    def test_download_lazy_initial_version(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        self.assertFalse(versioner.has_initial_version())

        browser.open(self.document, view='download_file_version', data={'version_id': 0})
        self.assertEqual(self.document.file.data, browser.contents)

    @browsing
    def test_requires_version_id(self, browser):
        self.login(self.regular_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.document, view='download_file_version')

        self.assertEqual(
            u'Missing parameter "version_id".', cm.exception.message
        )

    @browsing
    def test_requires_valid_version_id(self, browser):
        self.login(self.regular_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.document,
                view='download_file_version',
                data={'version_id': 'foo'},
            )

        self.assertEqual(u'Invalid version id "foo".', cm.exception.message)

    @browsing
    def test_requires_existing_version_id(self, browser):
        self.login(self.regular_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.document,
                view='download_file_version',
                data={'version_id': '33'},
            )

        self.assertEqual('Version "33" does not exist.', cm.exception.message)

    @browsing
    def test_download_view_redirects_to_listing_for_missing_files(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.empty_document, view='download')
        self.assertEqual([u'Document L\xe4\xe4r has no file.'], error_messages())

    @browsing
    def test_download_view_downloads_working_copy_if_document_checked_out_by_current_user(self, browser):
        self.login(self.regular_user, browser)
        initDocumentData = self.document.file.data

        manager = getMultiAdapter(
            (self.document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        # Updating the file will create an initial version with the initial file content
        self.document.update_file('my working copy')
        browser.open(self.document, view='download')
        self.assertEqual('my working copy', browser.contents)
        self.assertNotEqual(initDocumentData, browser.contents)

    @browsing
    def test_download_view_raises_bad_request_if_trying_to_download_a_document_checked_out_by_another_user_without_a_version(self, browser):
        self.login(self.dossier_manager)
        manager = getMultiAdapter(
            (self.document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        self.login(self.regular_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.document, view='download')


class TestDocumentDownloadVersion(FunctionalTestCase):
    """We need a functional test to be able to commit the blob."""

    @browsing
    def test_download_versioned_copy_creates_journal_entries_with_versions_in_title(self, browser):
        browser.login()
        document = create(Builder('document').with_dummy_content())
        versioner = Versioner(document)
        versioner.create_version('Initial version')
        versioner.create_version('Some updates.')
        transaction.commit()

        browser.open(document, view='tabbedview_view-versions')
        browser.css('a.function-download-copy').first.click()
        browser.find('Download').click()
        self.assert_journal_entry(document, 'File copy downloaded', 'Document copy downloaded version 1')

        versioner.create_version('Oops.')
        transaction.commit()
        browser.open(document, view='tabbedview_view-versions')
        browser.css('a.function-download-copy').first.click()
        browser.find('Download').click()
        self.assert_journal_entry(document, 'File copy downloaded', 'Document copy downloaded version 2')

    @browsing
    def test_download_confirmation_view_for_version_download(self, browser):
        browser.login()
        document = create(Builder('document').with_dummy_content())
        versioner = Versioner(document)
        versioner.create_version('Initial version')
        versioner.create_version('Some updates.')
        transaction.commit()

        browser.open(document, view='file_download_confirmation', data={'version_id': 1})
        self.assertEqual(
            "You're downloading a copy of the document Testdokumaent.doc",
            browser.css(".details > p").first.text,
        )
        browser.find('Download').click()
        expected_url = "{}/download_file_version?version_id=1&error_as_message=1".format(document.absolute_url())
        self.assertEqual(expected_url, browser.url)
        self.assertEqual(document.file.data, browser.contents)

    @browsing
    def test_download_view_downloads_the_latest_version_if_the_document_is_checked_out_by_another_user(self, browser):
        self.login()
        document = create(Builder('document').with_dummy_content())
        initDocumentData = document.file.data

        self.grant("Manager")
        manager = getMultiAdapter(
            (document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        # Updating the file will create an initial version with the initial file content
        document.update_file('my working copy')
        transaction.commit()

        browser.login().open(document, view='download')
        self.assertEqual('my working copy', browser.contents)
        self.assertNotEqual(initDocumentData, browser.contents)

        # If document is checked out by someone else, download returns
        # last checked-in version.
        IAnnotations(document)['opengever.document.checked_out_by'] = "hugo"
        transaction.commit()
        browser.login().open(document, view='download')
        self.assertEqual(initDocumentData, browser.contents)
