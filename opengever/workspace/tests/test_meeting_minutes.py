from ftw.testbrowser import browsing
from opengever.core.testing import WEASYPRINT_SERVICE_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase
from opengever.workspace.browser.meeting_pdf import MeetingMinutesPDFView
from zope.globalrequest import getRequest


class TestMeetingMinutes(IntegrationTestCase):

    layer = WEASYPRINT_SERVICE_INTEGRATION_TESTING

    @browsing
    def test_meeting_minutes_pdf_view_returns_a_pdf(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, view="meeting_minutes_pdf")
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.headers['Content-Type'], 'application/pdf')
        self.assertEqual(browser.contents[:8], '%PDF-1.5')

    @browsing
    def test_related_items_included_in_meeting_minutes_html(self, browser):
        self.login(self.workspace_member, browser)
        view = MeetingMinutesPDFView(self.workspace_meeting, getRequest())
        html = view.meeting_minutes_html()
        browser.parse(html)

        self.assertEqual(['Decision:', 'Related items:'], browser.css('h3').text)
        self.assertEqual(['Teamraumdokument'], browser.css('ul.related_items a').text)
        self.assertEqual(self.workspace_document.absolute_url(),
                         browser.css('ul.related_items a')[0].get('href'))
