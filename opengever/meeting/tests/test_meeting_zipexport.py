from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.meeting.browser.protocol import GenerateProtocol
from opengever.testing import IntegrationTestCase
from StringIO import StringIO
import cgi


class TestMeetingZipExportView(IntegrationTestCase):
    features = ('meeting',)

    @browsing
    def test_zip_export_generate_protocol_if_there_is_none(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertFalse(self.meeting.model.has_protocol_document())
        self.assertIn('Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_includes_generated_protocol(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(GenerateProtocol.url_for(self.meeting.model))
        self.assertTrue(self.meeting.model.has_protocol_document())

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_generate_protocol_if_outdated(self, browser):
        self.activate_feature('word-meeting')
        self.login(self.committee_responsible, browser)
        browser.open(GenerateProtocol.url_for(self.meeting.model))

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
                      zip_file.namelist())

        browser.open(self.meeting, view='edit-meeting')
        browser.fill({'Title': 'New Meeting Title'}).save()

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Agendaitem list-New Meeting Title.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_attachments(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            '1. Vertragsentwurf fur weitere Bearbeitung bewilligen/Vertragsentwurf.docx',
            zip_file.namelist())

    @browsing
    def test_export_proposal_word_documents(self, browser):
        self.activate_feature('word-meeting')
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            '1. Anderungen am Personalreglement/Anderungen am Personalreglement.docx',
            zip_file.namelist())

    @browsing
    def test_excerpt_is_not_exported(self, browser):
        self.activate_feature('word-meeting')
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_word_proposal)
        agenda_item.decide()
        agenda_item.generate_excerpt(title='Ahoi McEnroe!')

        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertEquals(
            ['Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
             '1. Anderungen am Personalreglement/Vertragsentwurf.docx',
             '1. Anderungen am Personalreglement/Anderungen am Personalreglement.docx',
             'Agendaitem list-9. Sitzung der Rechnungsprufungskommission.docx',
             'meeting.json'],
            zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_list(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting, view='export-meeting-zip')
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            'Agendaitem list-9. Sitzung der Rechnungsprufungskommission.docx',
            zip_file.namelist())

    @browsing
    def test_zip_export_link_on_meeting_view(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertTrue(browser.css('a.download-zipexport-btn'))
        self.assertEquals(
            'Export as Zip',
            browser.css('.item.zip-download > .title').first.text)

        browser.css('a.download-zipexport-btn').first.click()
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertIsNone(zip_file.testzip(),
                          'Got a invalid zip file.')
        self.assertEquals(
            '9. Sitzung der Rechnungsprufungskommission.zip',
            cgi.parse_header(browser.headers['content-disposition'])[1]['filename'],
            'Wrong zip filename.')
