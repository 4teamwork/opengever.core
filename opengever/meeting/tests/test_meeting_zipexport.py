from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from ftw.zipexport.zipfilestream import ZipFile
from mock import patch
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import localized_datetime
from StringIO import StringIO
import cgi
import json


DOCUMENT_CHECKSUM = '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2'


def mocked_bumblebee_request(*args, **kwargs):
    class MockResponse:
        def __init__(self, file_data, status_code):
            self.file_data = file_data
            self.status_code = status_code

        def __iter__(self):
            yield self.file_data

        def json(self):
            return self.json_data

    # Handle self.document as not available on bumblebee
    url = args[0]
    if DOCUMENT_CHECKSUM in url:
        return MockResponse(None, 302)

    return MockResponse('PDF_DATA', 200)


class TestMeetingZipExportView(IntegrationTestCase):
    features = ('meeting',)

    @browsing
    def test_zip_export_generate_protocol_if_there_is_none(self, browser):
        self.login(self.committee_responsible, browser)

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')
            zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertFalse(self.meeting.model.has_protocol_document())
        self.assertIn('Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_includes_generated_protocol(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.update_protocol_document()
        self.assertTrue(self.meeting.model.has_protocol_document())

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')
            zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertIn('Protocol-9. Sitzung der Rechnungsprufungskommission.pdf',
                      zip_file.namelist())

    @browsing
    def test_zip_export_generate_protocol_if_outdated(self, browser):
        self.login(self.committee_responsible, browser)

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
                      zip_file.namelist())

        browser.open(self.meeting, view='edit-meeting')
        browser.fill({'Title': 'New Meeting Title'}).save()

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Agendaitem list-New Meeting Title.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_attachments(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            '1. Anderungen am Personalreglement/Vertragsentwurf.docx',
            zip_file.namelist())

    @browsing
    def test_export_proposal_word_documents(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            '1. Anderungen am Personalreglement/Anderungen am Personalreglement.pdf',
            zip_file.namelist())

    @browsing
    def test_excerpt_is_not_exported(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_word_proposal)
        agenda_item.decide()
        agenda_item.generate_excerpt(title='Ahoi McEnroe!')

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertEquals(
            ['Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
             '1. Anderungen am Personalreglement/Vertragsentwurf.docx',
             '1. Anderungen am Personalreglement/Anderungen am Personalreglement.pdf',
             'Agendaitem list-9. Sitzung der Rechnungsprufungskommission.docx',
             'meeting.json'],
            zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_list(self, browser):
        self.login(self.committee_responsible, browser)
        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn(
            'Agendaitem list-9. Sitzung der Rechnungsprufungskommission.docx',
            zip_file.namelist())

    @browsing
    def test_zip_export_link_on_meeting_view(self, browser):
        self.login(self.committee_responsible, browser)
        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting)

        editbar.menu_option('Actions', 'Export as Zip').click()

        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertIsNone(zip_file.testzip(),
                          'Got a invalid zip file.')
        self.assertEquals(
            '9. Sitzung der Rechnungsprufungskommission.zip',
            cgi.parse_header(browser.headers['content-disposition'])[1]['filename'],
            'Wrong zip filename.')

    @browsing
    def test_meeting_can_be_exported_to_zip_when_agenda_item_list_template_is_missing(self, browser):
        self.login(self.committee_responsible, browser)
        self.committee.agendaitem_list_template = None
        self.committee_container.agendaitem_list_template = None
        browser.open(self.meeting, view='export-meeting-zip')
        statusmessages.assert_no_error_messages()
        self.assertEquals('application/zip', browser.contenttype)

    @browsing
    def test_exported_meeting_contains_json(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting, view='export-meeting-zip')
        self.assertEquals('application/zip', browser.contenttype)

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertEquals(
            ['Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
             'Agendaitem list-9. Sitzung der Rechnungsprufungskommission.docx',
             'meeting.json'],
            zip_file.namelist())

    def test_meeting_data_for_zip_export_json(self):
        self.login(self.committee_responsible)
        self.schedule_paragraph(self.meeting, u'A Gesch\xfcfte')
        with freeze(localized_datetime(2017, 12, 13)):
            self.schedule_ad_hoc(self.meeting, u'Ad-hoc Traktand\xfem')
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        self.assertEquals({
            'agenda_items': [{
                'title': u'A Gesch\xfcfte',
            }, {
                'number': '1.',
                'proposal': {
                    'checksum': 'e00d6c8fb32c30d3ca3a3f8e5d873565482567561023016d9ca18243ff1cfa14',
                    'file': u'1. Ad-hoc Traktandthm/Ad hoc agenda item Ad-hoc Traktandthm.docx',
                    'modified': u'2017-12-12T23:00:00+01:00',
                },
                'title': u'Ad-hoc Traktand\xfem',
            }, {
                'attachments': [{
                    'checksum': '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
                    'file': u'2. Anderungen am Personalreglement/Vertragsentwurf.docx',
                    'modified': u'2016-08-31T15:21:46+02:00',
                    'title': u'Vertr\xe4gsentwurf',
                }],
                'number': '2.',
                'proposal': {
                    'checksum': 'e00d6c8fb32c30d3ca3a3f8e5d873565482567561023016d9ca18243ff1cfa14',
                    'file': u'2. Anderungen am Personalreglement/Anderungen am Personalreglement.docx',
                    'modified': u'2016-08-31T15:21:44+02:00',
                },
                'title': u'\xc4nderungen am Personalreglement',
            }],
            'committee': {
                'oguid': u'plone:1009233300',
                'title': u'Rechnungspr\xfcfungskommission',
            },
            'end': u'2016-09-12T17:00:00+00:00',
            'location': u'B\xfcren an der Aare',
            'start': u'2016-09-12T15:30:00+00:00',
            'title': u'9. Sitzung der Rechnungspr\xfcfungskommission',
        }, self.meeting.get_data_for_zip_export())

    @browsing
    def test_exported_meeting_json_has_correct_file_names(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_paragraph(self.meeting, u'A Gesch\xfcfte')
        with freeze(localized_datetime(2017, 12, 13)):
            self.schedule_ad_hoc(
                self.meeting, u'Ad-hoc Traktand\xfem'
            ).decide()
        self.schedule_proposal(
            self.meeting, self.submitted_word_proposal
        ).decide()
        with freeze(localized_datetime(2017, 12, 14)):
            self.meeting.model.close()

        with patch('requests.get', side_effect=mocked_bumblebee_request):
            browser.open(self.meeting, view='export-meeting-zip')
            self.assertEquals('application/zip', browser.contenttype)

            zip_file = ZipFile(StringIO(browser.contents), 'r')
            meeting_json = json.loads(zip_file.read('meeting.json'))

        # the protocol is generated during the tests and its checksum cannot
        # be predicted
        meeting_json['meetings'][0]['protocol']['checksum'] = 'unpredictable'

        self.assert_json_structure_equal({
            'meetings': [
                {'agenda_items': [
                    {'title': u'A Gesch\xfcfte'},
                    {'number': '1.',
                     'proposal': {
                         'checksum': 'e00d6c8fb32c30d3ca3a3f8e5d873565482567561023016d9ca18243ff1cfa14',
                         'file': '1. Ad-hoc Traktandthm/Ad hoc agenda item Ad-hoc Traktandthm.docx',
                         'modified': '2017-12-12T23:00:00+01:00'
                     },
                     'title': u'Ad-hoc Traktand\xfem'},
                    {'attachments': [{
                        'checksum': '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
                        'file': '2. Anderungen am Personalreglement/Vertragsentwurf.docx',
                        'modified': '2016-08-31T15:21:46+02:00',
                        'title': u'Vertr\xe4gsentwurf'}],
                     'number': '2.',
                     'proposal': {
                         'checksum': 'e00d6c8fb32c30d3ca3a3f8e5d873565482567561023016d9ca18243ff1cfa14',
                         'file': '2. Anderungen am Personalreglement/Anderungen am Personalreglement.docx',
                         'modified': '2016-08-31T15:21:44+02:00'
                     },
                     'title': u'\xc4nderungen am Personalreglement'}
                 ],
                 'committee': {'oguid': 'plone:1009233300',
                               'title': u'Rechnungspr\xfcfungskommission'},
                 'end': '2016-09-12T17:00:00+00:00',
                 'location': u'B\xfcren an der Aare',
                 'protocol': {
                     'checksum': 'unpredictable',
                     'file': 'Protocol-9. Sitzung der Rechnungsprufungskommission.docx',
                     'modified': '2017-12-13T23:00:00+01:00'
                 },
                 'start': '2016-09-12T15:30:00+00:00',
                 'title': u'9. Sitzung der Rechnungspr\xfcfungskommission'}
                ],
            'version': '1.0.0'
            }, meeting_json)

        file_names = zip_file.namelist()

        for file_name in [
                '1. Ad-hoc Traktandthm/Ad hoc agenda item Ad-hoc Traktandthm.pdf',
                '2. Anderungen am Personalreglement/Anderungen am Personalreglement.pdf',
                'Protocol-9. Sitzung der Rechnungsprufungskommission.pdf']:
            self.assertIn(file_name, file_names)

        # The pdf is not avaible on bumblebee see `mocked_bumblebee_request`
        self.assertIn(
            '2. Anderungen am Personalreglement/Vertragsentwurf.docx', file_names)
        self.assertNotIn(
            '2. Anderungen am Personalreglement/Vertragsentwurf.pdf', file_names)

        # assert file data
        self.assertEquals(
            'PDF_DATA',
            zip_file.read('Protocol-9. Sitzung der Rechnungsprufungskommission.pdf'))
        self.assertNotEquals(
            'PDF_DATA',
            zip_file.read('2. Anderungen am Personalreglement/Vertragsentwurf.docx'))
