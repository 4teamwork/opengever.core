from ftw.testbrowser import browsing
from opengever.dossier.tests.test_overview import TestOverview


class TestMeetingDossierOverview(TestOverview):

    @browsing
    def test_meeting_is_linked_on_overview(self, browser):
        self.login(self.meeting_user, browser)

        browser.login().open(self.meeting_dossier, view='tabbedview_view-overview')

        link = browser.css('#linked_meetingBox a').first
        self.assertEqual(
            u'9. Sitzung der Rechnungspr\xfcfungskommission', link.text)
