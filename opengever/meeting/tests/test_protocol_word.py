from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase


class TestProtocolWithWord(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_word_protocols_can_be_created_and_updated(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        meeting = self.meeting.model

        self.assertIsNone(meeting.protocol_document)

        browser.open(meeting.get_url())
        # generate first protocol
        browser.css('.generate-protocol').first.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been generated '
            u'successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(0, meeting.protocol_document.generated_version)

        # update already generated protocol
        browser.css('.refresh-protocol').first.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been updated successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(1, meeting.protocol_document.generated_version)
