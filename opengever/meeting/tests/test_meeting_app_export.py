from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestMeetingAppExportView(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_button_displayed_on_meeting_view(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertTrue(browser.css('a.actionicon-object_buttons-export-meeting-app'))
        self.assertEquals(
            'Export to meeting application',
            browser.css('a.actionicon-object_buttons-export-meeting-app > .subMenuTitle').first.text)
