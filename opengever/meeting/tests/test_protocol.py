from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase


class TestProtocol(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_word_protocols_can_be_created_and_updated(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_paragraph(self.meeting, u'A-Gesch\xe4fte')
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        meeting = self.meeting.model

        self.assertIsNone(meeting.protocol_document)

        browser.open(meeting.get_url())
        # generate first protocol
        browser.css('.meeting-document.protocol-doc .action.generate').first.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been generated '
            u'successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(u'Protocol-9. Sitzung der Rechnungspruefungskommission.docx',
                         meeting.protocol_document.resolve_document().file.filename)
        self.assertEqual(0, meeting.protocol_document.generated_version)

        # update already generated protocol
        browser.css('.meeting-document.protocol-doc .action.generate').first.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been updated successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(1, meeting.protocol_document.generated_version)

    @browsing
    def test_protocol_generate_action_only_available_for_unedited_protocols(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_paragraph(self.meeting, u'A-Gesch\xe4fte')
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        meeting = self.meeting.model

        self.assertIsNone(meeting.protocol_document)

        browser.open(meeting.get_url())
        # generate first protocol
        generate_button = browser.css('.meeting-document.protocol-doc .action.generate').first
        # Make sure we have the action without overwrite
        self.assertIn("overwrite=False", generate_button.get("href"))
        generate_button.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been generated '
            u'successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(0, meeting.protocol_document.generated_version)

        # Fake editing the protocol
        document = meeting.protocol_document.resolve_document()
        versioner = Versioner(document)
        versioner.create_initial_version()
        versioner.create_version("bumb version")

        # Without reloading the page, we still have the link to update the protocol
        # without confirmation
        generate_button = browser.css('.meeting-document.protocol-doc .action.generate').first
        # Make sure we have the action without overwrite
        self.assertIn("overwrite=False", generate_button.get("href"))
        generate_button.click()
        # Protocol was not updated, as update needs confirmation
        self.assertEqual(0, meeting.protocol_document.generated_version)
        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der Rechnungspr\xfcfungskommission '
            'has not been updated. The protocol has been modified manually and '
            'these modifications will be lost if you regenerate the protocol.')

        # Reload browser page and make sure we now have the link with confirmation
        browser.open(meeting.get_url())
        generate_button = browser.css('.meeting-document.protocol-doc .action.generate').first
        self.assertIn("overwrite=True", generate_button.get("href"))
        self.assertEqual('generate_protocol_with_confirm', generate_button.get("id"))
        generate_button.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been updated successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(2, meeting.protocol_document.generated_version)

    @browsing
    def test_word_protocols_with_suffix_template_in_committee_can_be_created_and_updated(self, browser):
        self.login(self.committee_responsible, browser)
        self.committee.protocol_suffix_template = self.committee.protocol_header_template
        self.schedule_paragraph(self.meeting, u'A-Gesch\xe4fte')
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        meeting = self.meeting.model

        self.assertIsNone(meeting.protocol_document)

        browser.open(meeting.get_url())
        # generate first protocol
        browser.css('.meeting-document.protocol-doc .action.generate').first.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been generated '
            u'successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(0, meeting.protocol_document.generated_version)

        # update already generated protocol
        browser.css('.meeting-document.protocol-doc .action.generate').first.click()

        statusmessages.assert_message(
            u'Protocol for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been updated successfully.')
        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(1, meeting.protocol_document.generated_version)

    @browsing
    def test_protocol_is_generated_when_closing_meetings(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)

        meeting = self.meeting.model

        self.assertIsNone(meeting.protocol_document)

        browser.open(meeting.get_url())
        browser.find('Close meeting').click()
        statusmessages.assert_no_error_messages()

        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(0, meeting.protocol_document.generated_version)
