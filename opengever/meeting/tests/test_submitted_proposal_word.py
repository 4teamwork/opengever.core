from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase


class TestSubmittedProposal(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_submitted_proposal_edit_view_display_word_fields_only(self, browser):
        word_fields = [u'Title']
        self.login(self.committee_responsible, browser)
        browser.visit(self.submitted_proposal, view='edit')
        self.assertEquals(
            word_fields,
            browser.css('form#form > div.field > label').text)
