from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.testing import IntegrationTestCase
from StringIO import StringIO


class TestMeetingDebugViews(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_smoke_debug_docxcompose(self, browser):
        self.login(self.manager, browser)

        self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.schedule_ad_hoc(self.meeting, "Foo")
        self.schedule_paragraph(self.meeting, "Bar")

        browser.open(self.meeting, view='debug_docxcompose')
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertIsNone(zip_file.testzip(),
                          'Got a invalid zip file.')

    @browsing
    def test_smoke_debug_excerpt_docxcompose(self, browser):
        self.login(self.manager, browser)

        agenda_1 = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        agenda_2 = self.schedule_ad_hoc(self.meeting, "Foo")
        agenda_paragraph = self.schedule_paragraph(self.meeting, "Bar")

        browser.open(self.agenda_item_url(agenda_1, 'debug_excerpt_docxcompose'))
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIsNone(zip_file.testzip(),
                          'Got a invalid zip file.')

        browser.open(self.agenda_item_url(agenda_2, 'debug_excerpt_docxcompose'))
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIsNone(zip_file.testzip(),
                          'Got a invalid zip file.')

        with browser.expect_http_error(404):
            browser.open(self.agenda_item_url(
                agenda_paragraph, 'debug_excerpt_docxcompose'))
