from ftw.testbrowser import browsing
from opengever.dossier.tests import test_overview


class TestMeetingDossierOverview(test_overview.TestOverview):

    @property
    def tested_dossier(self):
        return self.meeting_dossier

    @property
    def tested_document(self):
        return self.meeting_document

    @property
    def tested_task(self):
        return self.meeting_task

    @property
    def tested_subtask(self):
        return self.meeting_subtask

    @property
    def participants(self):
        return [u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                u'M\xfcller Fr\xe4nzi (franzi.muller)']

    @property
    def task_titles(self):
        return [u'Programm \xdcberpr\xfcfen',
                u'H\xf6rsaal reservieren']

    @property
    def task_titles_minus_pending(self):
        return [u'Programm \xdcberpr\xfcfen']

    @browsing
    def test_meeting_is_linked_on_overview(self, browser):
        self.login(self.meeting_user, browser)

        browser.visit(self.meeting_dossier, view='tabbedview_view-overview')

        link = browser.css('#linked_meetingBox a').first
        self.assertEqual(
            u'9. Sitzung der Rechnungspr\xfcfungskommission', link.text)
