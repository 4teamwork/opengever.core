from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.zipexport.zipfilestream import ZipFile
from opengever.meeting.browser.meetings.agendaitem_list import GenerateAgendaItemList
from opengever.testing import IntegrationTestCase
from opengever.testing import set_preferred_language
from StringIO import StringIO


class TestMeetingZipExportView(IntegrationTestCase):
    features = ('meeting',)
    maxDiff = None

    @browsing
    def test_zip_export_includes_generated_protocol(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.update_protocol_document()
        self.assertTrue(self.meeting.model.has_protocol_document())

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Protocol-9. Sitzung der Rechnungspruefungskommission.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_includes_generated_agenda_item_list_document(self, browser):
        self.login(self.committee_responsible, browser)
        self.generate_agenda_item_list(self.meeting)
        self.assertTrue(self.meeting.model.has_agendaitem_list_document())

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Agendaitem list-9. Sitzung der Rechnungspruefungskommission.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_attachments(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_proposal)

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            'Traktandum 1/Beilage/1_Vertraegsentwurf.docx',
            zip_file.namelist())

    @browsing
    def test_zip_export_skips_agenda_items_attachments_without_file(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.committee_responsible, browser)

        self.proposal.submit_additional_document(self.empty_document)
        self.proposal.submit_additional_document(self.subdocument)
        self.schedule_proposal(self.meeting, self.submitted_proposal)

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertItemsEqual(
            ['Traktandum 1/Vertraege.docx',
             'Traktandum 1/Beilage/1_Vertraegsentwurf.docx',
             'Traktandum 1/Beilage/2_Uebersicht der Vertraege von 2016.xlsx'],
            zip_file.namelist())

    @browsing
    def test_export_proposal_word_documents(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            'Traktandum 1/Vertraege.docx',
            zip_file.namelist())

    @browsing
    def test_excerpt_is_not_exported(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()
        agenda_item.generate_excerpt(title='Ahoi McEnroe!')

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertItemsEqual(
            ['Traktandum 1/Beilage/1_Vertraegsentwurf.docx',
             'Traktandum 1/Vertraege.docx'],
            zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_list(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(GenerateAgendaItemList.url_for(self.meeting.model))
        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            'Agendaitem list-9. Sitzung der Rechnungspruefungskommission.docx',
            zip_file.namelist())

    @browsing
    def test_meeting_can_be_exported_to_zip_when_proposal_related_to_mail(self, browser):
        self.login(self.committee_responsible, browser)

        submitted_proposal = create(
            Builder('proposal')
            .within(self.dossier)
            .having(
                title=u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen',
                committee=self.committee.load_model(),
            )
            .relate_to(self.mail_eml)
            .as_submitted()
        )

        self.schedule_proposal(self.meeting, submitted_proposal)

        browser.open(self.meeting, view='export-meeting-zip')
        statusmessages.assert_no_error_messages()
        self.assertEquals('application/zip', browser.contenttype)

    @browsing
    def test_meeting_can_be_exported_to_zip_when_agenda_item_list_template_is_missing(self, browser):
        self.login(self.committee_responsible, browser)
        self.committee.agendaitem_list_template = None
        self.committee_container.agendaitem_list_template = None
        browser.open(self.meeting, view='export-meeting-zip')
        statusmessages.assert_no_error_messages()
        self.assertEquals('application/zip', browser.contenttype)

    @browsing
    def test_filename_conflicts_are_avoided_by_prefixing_attachment_number(self, browser):
        set_preferred_language(self.portal.REQUEST, 'de-ch')
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.committee_responsible, browser)

        documents = [
            create(Builder('document')
                   .within(self.dossier)
                   .titled('The same title')
                   .with_dummy_content())
            for i in range(3)]
        proposal, submitted_proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(committee=self.committee.load_model())
                          .with_submitted()
                          .relate_to(*documents))
        self.schedule_proposal(self.meeting, submitted_proposal)

        browser.open(self.meeting, view='export-meeting-zip')
        self.assertEquals('application/zip', browser.contenttype)
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        expected_file_names = [u'Traktandum 1/Beilage/1_The same title.doc',
                               u'Traktandum 1/Beilage/2_The same title.doc',
                               u'Traktandum 1/Beilage/3_The same title.doc',
                               u'Traktandum 1/Fooo.docx']

        file_names = zip_file.namelist()
        self.assertItemsEqual(expected_file_names, file_names)
