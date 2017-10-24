from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.pages import editbar
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
    def test_no_meeting_dossier_link_if_no_permission(self, browser):
        self.login(self.dossier_responsible, browser)
        self.meeting_dossier.__ac_local_roles_block__ = True
        self.meeting_dossier.reindexObjectSecurity()

        self.login(self.meeting_user, browser)
        browser.open(self.meeting)
        with self.assertRaises(NoElementFound):
            browser.click_on('Sitzungsdossier 9/2017')

    @browsing
    def test_agenda_item_url(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.meeting)
        browser.css('.generate-agendaitem-list').first.click()
        link = browser.css('.download-agendaitem-list-btn').first

        self.assertEquals(
            self.meeting.model.agendaitem_list_document.get_download_url(),
            link.attrib['href'])

    @browsing
    def test_close_transition_closes_meeting(self, browser):
        self.login(self.committee_responsible, browser)
        self.assertEquals('pending', self.meeting.model.get_state().name)
        browser.open(self.meeting)
        editbar.menu_option('Actions', 'Close meeting').click()
        self.assertEquals('closed', self.meeting.model.get_state().name)

    @browsing
    def test_meeting_member_cannot_return_excerpt(self, browser):
        with self.login(self.committee_responsible, browser):
            agenda_item = self.schedule_proposal(self.meeting,
                                                 self.submitted_word_proposal)
            agenda_item.decide()
            agenda_item.generate_excerpt(title='The Excerpt')
            browser.open(self.meeting, view='agenda_items/list')
            self.assertIn('return_link', browser.json['items'][0]['excerpts'][0])

        self.login(self.meeting_user, browser)
        browser.open(self.meeting, view='agenda_items/list')
        self.assertNotIn('return_link', browser.json['items'][0]['excerpts'][0])
