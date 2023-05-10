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

    @browsing
    def test_meeting_minutes_header_uses_definition_on_workspace(self, browser):
        self.login(self.workspace_member, browser)

        self.workspace.meeting_template_header = {
            'left': '4teamwork AG',
            'center': '',
            'right': 'Musterstrasse 43',
        }

        view = MeetingMinutesPDFView(self.workspace_meeting, getRequest())
        html = view.meeting_minutes_html()

        expected_header = """
  @top-left {
    content: "4teamwork AG";
    white-space: pre;
  }
  @top-center {
    content: "";
    white-space: pre;
  }
  @top-right {
    content: "Musterstrasse 43";
    white-space: pre;
  }
"""
        self.assertIn(expected_header, html)

    @browsing
    def test_meeting_minutes_footer_uses_definition_on_workspace(self, browser):
        self.login(self.workspace_member, browser)

        self.workspace.meeting_template_footer = {
            'left': '4teamwork AG',
            'center': 'Musterstrasse 43',
            'right': '3001 Bern',
        }

        view = MeetingMinutesPDFView(self.workspace_meeting, getRequest())
        html = view.meeting_minutes_html()

        expected_header = """
  @bottom-left {
    content: "4teamwork AG";
    white-space: pre;
  }
  @bottom-center {
    content: "Musterstrasse 43";
    white-space: pre;
  }
  @bottom-right {
    content: "3001 Bern";
    white-space: pre;
  }
"""
        self.assertIn(expected_header, html)

    @browsing
    def test_meeting_minutes_header_dynamic_content(self, browser):
        self.login(self.workspace_member, browser)

        self.workspace.meeting_template_header = {
            'left': '{print_date}',
            'center': '',
            'right': '{page_number} / {number_of_pages}',
        }

        with freeze(datetime(2023, 5, 10)):
            view = MeetingMinutesPDFView(self.workspace_meeting, getRequest())
            html = view.meeting_minutes_html()

        expected_header = """
  @top-left {
    content: "May 10, 2023";
    white-space: pre;
  }
  @top-center {
    content: "";
    white-space: pre;
  }
  @top-right {
    content: ""counter(page)" / "counter(pages)"";
    white-space: pre;
  }
"""

        self.assertIn(expected_header, html)
