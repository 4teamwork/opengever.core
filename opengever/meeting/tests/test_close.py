from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestCloseMeeting(IntegrationTestCase):

    maxDiff = None

    features = ('meeting',)

    @browsing
    def test_proposalhistory_is_added(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_word_proposal)
        agenda_item.close()

        browser.open(self.meeting)
        browser.find('Close meeting').click()

        browser.open(self.submitted_word_proposal, view=u'tabbedview_view-overview')
        entry = browser.css('.answer').first

        self.assertEquals(u'Proposal decided by M\xfcller Fr\xe4nzi (franzi.muller)',
                          entry.css('h3').first.text)
        self.assertEquals('answer decided', entry.get('class'))

    @browsing
    def test_states_are_updated(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_word_proposal)
        agenda_item.close()

        browser.open(self.meeting)
        browser.find('Close meeting').click()

        self.assertEquals('closed', self.meeting.model.get_state().name)
        self.assertEquals('decided', self.word_proposal.get_state().name)
        self.assertEquals('decided', self.submitted_word_proposal.get_state().name)

    @browsing
    def test_redirects_to_meeting_and_show_statusmessage(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        browser.find('Close meeting').click()

        self.assertEquals(
          {
            "redirectUrl": u"http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view",
            "messages": [{
              "messageTitle": "Information",
              "message": "Transition Close meeting executed",
              "messageClass": "info"}]
          }, browser.json
        )
