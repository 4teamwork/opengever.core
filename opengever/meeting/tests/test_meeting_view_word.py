from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.meeting.tests.pages import meeting_view
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import byline


class TestWordMeetingView(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_meeting_metadata_is_visible(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        self.maxDiff = None
        self.assertEquals(
            [('State:', 'Pending'),
             ('Start:', 'Sep 12, 2016 05:30 PM'),
             ('End:', 'Sep 12, 2016 07:00 PM'),
             ('Presidency:', u'Sch\xf6ller Heidrun'),
             ('Secretary:', u'M\xfcller Henning'),
             ('Location:', u'B\xfcren an der Aare'),
             ('Meeting dossier:', 'Sitzungsdossier 9/2017')],
            byline.text_items())

        self.assertEquals(
            [['Meeting number:', ''],
             ['Participants:', u'Wendler Jens (jens-wendler@gmail.com)'
              u' W\xf6lfl Gerda (g.woelfl@hotmail.com)'],
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
