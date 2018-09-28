from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase


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
        browser.find('label_download').click()
        self.assert_journal_entry(self.document, 'File copy downloaded', 'Download copy current version (1)')

    @browsing
    def test_download_versioned_copy_creates_journal_entries_with_versions_in_title(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version')
        versioner.create_version('Some updates.')
        browser.open(self.document, view='tabbedview_view-versions')
        browser.css('a.function-download-copy').first.click()
        browser.find('label_download').click()
        self.assert_journal_entry(self.document, 'File copy downloaded', 'Download copy version 1')
        versioner.create_version('Oops.')
        browser.open(self.document, view='tabbedview_view-versions')
        browser.css('a.function-download-copy').first.click()
        browser.find('label_download').click()
        self.assert_journal_entry(self.document, 'File copy downloaded', 'Download copy version 2')

    @browsing
    def test_download_copy_without_overlay_creates_journal_entry(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version.')
        DownloadConfirmationHelper(self.document).deactivate()
        browser.open(self.document, view='tabbed_view/listing', data={'view_name': 'overview'})
        browser.find('Download copy').click()
        self.assert_journal_entry(self.document, 'File copy downloaded', 'Download copy current version (0)')

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
        self.assertEqual([u'The Document L\xe4\xe4r has no File.'], warning_messages())

    @browsing
    def test_download_confirmation_view_for_download(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='file_download_confirmation')
        self.assertEqual(
            "You're downloading a copy of the document Vertraegsentwurf.docx",
            browser.css(".details > p").first.text,
        )
        browser.find('label_download').click()
        self.assertEqual("{}/download".format(self.document.absolute_url()), browser.url)
        self.assertEqual(self.document.file.data, browser.contents)

    @browsing
    def test_download_confirmation_view_for_version_download(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version')
        versioner.create_version('Some updates.')
        browser.open(self.document, view='file_download_confirmation', data={'version_id': 1})
        self.assertEqual(
            "You're downloading a copy of the document Vertraegsentwurf.docx",
            browser.css(".details > p").first.text,
        )
        browser.find('label_download').click()
        expected_url = "{}/download_file_version?version_id=1".format(self.document.absolute_url())
        self.assertEqual(expected_url, browser.url)
        self.assertEqual(self.document.file.data, browser.contents)

    @browsing
    def test_download_view_redirects_to_listing_for_missing_files(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.empty_document, view='download')
        self.assertEqual([u'The Document L\xe4\xe4r has no File.'], error_messages())
