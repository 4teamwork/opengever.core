from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.testing import FunctionalTestCase


class TestDocumentCopyDownload(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentCopyDownload, self).setUp()
        self.document = create(Builder('document').with_dummy_content())

    def tearDown(self):
        dc_helper = DownloadConfirmationHelper()
        dc_helper.activate()
        super(TestDocumentCopyDownload, self).tearDown()

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
