from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import byline
import pytz


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

    @browsing
    def test_meeting_dossier_link(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        browser.click_on('Sitzungsdossier 9/2017')
        self.assertEquals(self.meeting_dossier.absolute_url(), browser.url)

    @browsing
    def test_agenda_items_list_document(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.meeting)
        docnode = browser.css('.meeting-document.agenda-item-list-doc').first
        self.assertFalse(docnode.css('div.document-label a'))
        self.assertEquals('Agenda item list', docnode.css('.document-label').first.text)
        self.assertEquals('Not yet generated.', docnode.css('.document-created').first.text)
        self.assertTrue(docnode.css('.action.generate'))
        self.assertFalse(docnode.css('.action.download'))

        with freeze(datetime(2016, 9, 2, 10, 15, 1, tzinfo=pytz.UTC)) as clock:
            docnode.css('.action.generate').first.click()
            docnode = browser.css('.meeting-document.agenda-item-list-doc').first
            self.assertTrue(docnode.css('div.document-label a'))
            self.assertEquals('Agenda item list', docnode.css('.document-label').first.text)
            self.assertEquals('Created at Sep 02, 2016 11:15 AM', docnode.css('.document-created').first.text)
            self.assertTrue(docnode.css('.action.generate'))
            self.assertTrue(docnode.css('.action.download'))

            self.assertEquals(self.meeting.model.agendaitem_list_document.get_download_url(),
                              docnode.css('.action.download').first.attrib['href'])

            clock.forward(hours=1)
            docnode.css('.action.generate').first.click()
            docnode = browser.css('.meeting-document.agenda-item-list-doc').first
            self.assertEquals('Created at Sep 02, 2016 12:15 PM', docnode.css('.document-created').first.text)

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
