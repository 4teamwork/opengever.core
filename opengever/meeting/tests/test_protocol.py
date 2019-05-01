from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from opengever.base.date_time import as_utc
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
import pytz


class TestProtocol(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_word_protocols_can_be_created_and_updated(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_paragraph(self.meeting, u'A-Gesch\xe4fte')
        self.schedule_proposal(self.meeting, self.submitted_proposal)
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

    def test_updating_word_protocol_will_update_modification_dates(self):
        self.login(self.committee_responsible)
        model = self.meeting.model

        creation_date = datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)
        update_date = datetime(2018, 10, 16, 0, 0, tzinfo=pytz.utc)

        # Generate first protocol
        with freeze(creation_date):
            model.update_protocol_document()

        document = model.protocol_document.resolve_document()

        self.assertEqual(creation_date, as_utc(document.modified().asdatetime()))
        self.assertEqual(creation_date, document.changed)

        # Update the protocol
        with freeze(update_date):
            model.update_protocol_document()

        self.assertEqual(update_date, as_utc(document.modified().asdatetime()))
        self.assertEqual(update_date, document.changed)

    @browsing
    def test_display_changed_property_as_last_modified_date(self, browser):
        self.login(self.committee_responsible, browser)
        model = self.meeting.model

        creation_date = datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)
        update_date = datetime(2018, 10, 16, 0, 0, tzinfo=pytz.utc)

        # Generate first protocol
        with freeze(creation_date):
            model.update_protocol_document()

        document = model.protocol_document.resolve_document()

        document.changed = update_date
        document.reindexObject(idxs=["changed"])

        self.assertEqual(creation_date, as_utc(document.modified().asdatetime()))
        self.assertEqual(update_date, document.changed)

        browser.open(self.meeting)

        self.assertEqual(
            'Modified at Oct 16, 2018 02:00 AM',
            browser.css('.protocol-doc .document-modified').first.text)

    @browsing
    def test_protocol_generate_action_only_available_for_unedited_protocols(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_paragraph(self.meeting, u'A-Gesch\xe4fte')
        self.schedule_proposal(self.meeting, self.submitted_proposal)
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
        self.schedule_proposal(self.meeting, self.submitted_proposal)
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
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)

        meeting = self.meeting.model

        self.assertIsNone(meeting.protocol_document)

        browser.open(meeting.get_url())
        browser.find('Close meeting').click()
        statusmessages.assert_no_error_messages()

        self.assertIsNotNone(meeting.protocol_document)
        self.assertEqual(0, meeting.protocol_document.generated_version)
