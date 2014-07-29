from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from zope.globalrequest import getRequest


class TestDocumentCopyDownload(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING
    use_browser = True

    def setUp(self):
        self.document = create(Builder('document'))

    def tearDown(self):
        dc_helper = DownloadConfirmationHelper(self.document, getRequest())
        dc_helper.activate()

    @browsing
    def test_disable_copy_download_overlay(self, browser):
        browser.login().open(self.document)

        self.assertEquals(1, len(browser.css('.link-overlay')))

        browser.css('.function-download-copy.link-overlay').first.click()
        browser.fill({"disable_download_confirmation": "on"}).submit()

        self.assertEquals(0, len(browser.css('.link-overlay')))
        self.assertFalse('file_download_confirmation' in browser.contents)
