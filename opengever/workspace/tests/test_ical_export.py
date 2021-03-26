from datetime import datetime
from ftw.testbrowser import browsing
from opengever.testing import assets
from opengever.testing import IntegrationTestCase


class TestMeetingMinutes(IntegrationTestCase):

    @browsing
    def test_meeting_ical_download(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, view="download_ical")

        self.assertEqual(browser.status_code, 200)
        self.assertEqual('text/calendar; charset=utf-8', browser.headers['Content-Type'])
        self.assertEqual('attachment; filename="meeting-1.ics"',
                         browser.headers['content-disposition'])

    @browsing
    def test_meeting_ical_download(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, view="download_ical")

        self.assertEqual(
            assets.load(u'ics_without_attendees.ics').replace('\n', '\r\n'),
            browser.contents)

    @browsing
    def test_meeting_ical_download_with_attendees(self, browser):
        self.login(self.workspace_member, browser)

        self.workspace_meeting.start = datetime(2021, 12, 8, 8, 30)
        self.workspace_meeting.end = datetime(2021, 12, 8, 10, 0)
        self.workspace_meeting.location = u'Sitzungszimmer 352, S\xfcdweststrasse, 3000 Bern'
        self.workspace_meeting.attendees = [
            self.workspace_owner.id, self.workspace_guest.id]

        browser.open(self.workspace_meeting, view="download_ical")

        self.assertEqual(
            assets.load(u'ics_with_attendees.ics').replace('\n', '\r\n'),
            browser.contents)
