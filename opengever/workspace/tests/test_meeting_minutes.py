from ftw.testbrowser import browsing
from opengever.base.interfaces import IDeleter
from opengever.core.testing import WEASYPRINT_SERVICE_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from opengever.workspace.browser.meeting_pdf import MeetingMinutesPDFView
from zope.globalrequest import getRequest


class TestMeetingMinutes(IntegrationTestCase):

    layer = WEASYPRINT_SERVICE_INTEGRATION_TESTING

    features = ('workspace', )

    @browsing
    def test_meeting_minutes_pdf_view_returns_a_pdf(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, view="meeting_minutes_pdf")
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.headers['Content-Type'], 'application/pdf')
        self.assertEqual(browser.contents[:8], '%PDF-1.7')

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

    @browsing
    def test_meeting_minutes_html_handles_broken_relations(self, browser):
        self.login(self.workspace_member, browser)

        # We delete the document referenced by the agendaitem
        ITrasher(self.workspace_document).trash()
        deleter = IDeleter(self.workspace_document)
        deleter.delete()

        view = MeetingMinutesPDFView(self.workspace_meeting, getRequest())
        html = view.meeting_minutes_html()
        browser.parse(html)

        self.assertEqual(['Decision:'], browser.css('h3').text)
        self.assertEqual([], browser.css('ul.related_items a').text)
