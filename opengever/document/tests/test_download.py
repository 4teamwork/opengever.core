from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.journal.browser import JournalHistory
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
import transaction


class TestDocumentDownloadConfirmation(FunctionalTestCase):
    """Test the document download confirmation overlay."""

    def setUp(self):
        super(TestDocumentDownloadConfirmation, self).setUp()
        login(self.portal, TEST_USER_NAME)
        self.document = create(Builder("document").titled(u'A letter for you'))

        file_ = NamedBlobFile('bla bla', filename=u'test.txt')
        self.document.file = file_

        # create version
        repo_tool = getToolByName(self.portal, 'portal_repository')
        repo_tool._recursiveSave(self.document, {},
                                 repo_tool._prepareSysMetadata('mock'),
                                 autoapply=repo_tool.autoapply)
        transaction.commit()

    def tearDown(self):
        DownloadConfirmationHelper().activate()
        super(TestDocumentDownloadConfirmation, self).tearDown()

    def assert_download_journal_entry_created(self, document):
        request = self.layer['request']

        journal = JournalHistory(document, request)
        entry = journal.data()[-1]
        translated_action_title = translate(entry['action']['title'],
                                            context=request)
        self.assertEqual(u'Download copy', translated_action_title)
        self.assertEquals(TEST_USER_ID, entry['actor'])
        self.assertDictContainsSubset({'type': 'File copy downloaded',
                                       'visible': True},
                                      entry['action'])

    @browsing
    def test_download_copy_with_overlay_creates_journal_entry(self, browser):
        browser.login().open(self.document,
                             view='tabbed_view/listing',
                             data={'view_name': 'overview'})

        browser.find('Download copy').click()
        browser.find('label_download').click()

        self.assert_download_journal_entry_created(self.document)

    @browsing
    def test_download_copy_without_overlay_creates_journal_entry(self, browser):  # noqa
        DownloadConfirmationHelper().deactivate()
        transaction.commit()

        browser.login().open(self.document,
                             view='tabbed_view/listing',
                             data={'view_name': 'overview'})

        browser.find('Download copy').click()

        self.assert_download_journal_entry_created(self.document)

    @browsing
    def test_disable_copy_download_overlay(self, browser):
        browser.login().open(self.document,
                             view='tabbed_view/listing',
                             data={'view_name': 'overview'})
        overview_link_selector = '.function-download-copy.link-overlay'
        self.assertEquals(1, len(browser.css('.link-overlay')))

        browser.css(overview_link_selector).first.click()
        browser.fill({"disable_download_confirmation": "on"}).submit()

        self.assertEquals(0, len(browser.css('.link-overlay')))
        self.assertFalse('file_download_confirmation' in browser.contents)

    @browsing
    def test_download_confirmation_for_empty_file(self, browser):
        self.document.file = None
        transaction.commit()

        browser.login().open(self.document, view='file_download_confirmation')
        self.assertEqual(['The Document A letter for you has no File.'],
                         warning_messages())

    @browsing
    def test_download_confirmation_view_for_download(self, browser):
        browser.login().open(self.document, view='file_download_confirmation')
        self.assertEqual("You're downloading a copy of the document test.txt",
                         browser.css(".details > p").first.text)

        browser.find('label_download').click()
        self.assertEqual("{}/download".format(self.document.absolute_url()),
                         browser.url)
        self.assertEqual('bla bla', browser.contents)

    @browsing
    def test_download_confirmation_view_for_version_download(self, browser):
        browser.login().open(self.document, view='file_download_confirmation',
                             data={'version_id': 1})

        self.assertEqual("You're downloading a copy of the document test.txt",
                         browser.css(".details > p").first.text)

        browser.find('label_download').click()
        expected_url = "{}/download_file_version?version_id=1".format(
            self.document.absolute_url())

        self.assertEqual(expected_url, browser.url)
        self.assertEqual('bla bla', browser.contents)

    @browsing
    def test_download_view_redirects_to_listing_for_missing_files(self, browser):  # noqa
        document = create(Builder('document').titled('No Document'))

        browser.login().open(document, view='download')
        self.assertEqual(['The Document No Document has no File.'],
                         error_messages())
