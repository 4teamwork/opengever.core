from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.testing import IntegrationTestCase
from StringIO import StringIO


class TestMeetingZipExportView(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_smoke_debug_docxcompose(self, browser):
        self.login(self.manager, browser)

        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        self.schedule_ad_hoc(self.meeting, "Foo")
        self.schedule_paragraph(self.meeting, "Bar")

        browser.open(self.meeting, view='debug_docxcompose')
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertIsNone(zip_file.testzip(),
                          'Got a invalid zip file.')
