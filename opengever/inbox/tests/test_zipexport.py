from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.testing import IntegrationTestCase
from StringIO import StringIO


class TestForwardingZipExport(IntegrationTestCase):

    @browsing
    def test_forwardings_with_documents_are_exported(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(self.inbox_forwarding, view='zip_export')
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertEqual(
            [self.inbox_forwarding_document.get_filename()],
            zip_file.namelist()
        )
