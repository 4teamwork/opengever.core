from ftw.testbrowser import browsing
from opengever.core.testing import WEASYPRINT_SERVICE_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase


class TestMeetingMinutes(IntegrationTestCase):

    layer = WEASYPRINT_SERVICE_INTEGRATION_TESTING

    @browsing
    def test_meeting_minutes_pdf_view_returns_a_pdf(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, view="meeting_minutes_pdf")
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.headers['Content-Type'], 'application/pdf')
        self.assertEqual(browser.contents[:8], '%PDF-1.5')
