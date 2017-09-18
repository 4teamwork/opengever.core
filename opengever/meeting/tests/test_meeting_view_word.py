from ftw.testbrowser import browsing
from opengever.meeting.tests.pages import meeting_view
from opengever.testing import IntegrationTestCase


class TestWordMeetingView(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_meeting_metadata_is_visible(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        self.maxDiff = None
        self.assertEquals(
            [['Status:', 'Pending'],
             ['Meeting start:', 'Sep 12, 2016 05:30 PM'],
             ['Meeting end:', 'Sep 12, 2016 07:00 PM'],
             ['Location:', u'B\xfcren an der Aare'],
             ['Meeting number:', ''],
             ['Presidency:', u'Sch\xf6ller Heidrun (h.schoeller@web.de)'],
             ['Secretary:', u'M\xfcller Henning (h.mueller@gmx.ch)'],
             ['Participants:', u'Wendler Jens (jens-wendler@gmail.com)'
              u' W\xf6lfl Gerda (g.woelfl@hotmail.com)'],
             ['Meeting dossier:', 'Sitzungsdossier 9/2017', ''],
             ['Agenda item list:', 'No agenda item list has been generated yet.', ''],
             ['Protocol:', 'No protocol has been generated yet.', '']],
            meeting_view.metadata())

    @browsing
    def test_meeting_dossier_link(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        browser.click_on('Sitzungsdossier 9/2017')
        self.assertEquals(self.meeting_dossier.absolute_url(), browser.url)

    @browsing
    def test_agenda_item_url(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.meeting)
        browser.css('.generate-agendaitem-list').first.click()
        link = browser.css('.download-agendaitem-list-btn').first

        self.assertEquals(
            self.meeting.model.agendaitem_list_document.get_download_url(),
            link.attrib['href'])
