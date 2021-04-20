from ftw.testbrowser import browsing
from ftw.testing import freeze
from ftw.zipexport.zipfilestream import ZipFile
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.meeting.zipexport import ZipJobManager
from opengever.testing import IntegrationTestCase
from opengever.testing import set_preferred_language
from opengever.testing.helpers import localized_datetime
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID
from StringIO import StringIO
import json


class TestPollMeetingZip(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    @browsing
    def test_zip_polling_view_reports_converting(self, browser):
        self.login(self.meeting_user, browser)

        job_manager = ZipJobManager(self.meeting.model)
        zip_job = job_manager.create_job()
        zip_job.add_doc_status(IUUID(self.document), {'status': 'converting'})

        browser.open(
            self.meeting,
            view='poll_meeting_zip?job_id={}'.format(zip_job.job_id),
            method='POST')
        self.assertEqual(1, browser.json['converting'])

    @browsing
    def test_zip_polling_view_creates_zip_when_all_finished(self, browser):
        self.login(self.meeting_user, browser)

        job_manager = ZipJobManager(self.meeting.model)
        zip_job = job_manager.create_job()
        zip_job.add_doc_status(
            IUUID(self.document),
            {'status': 'finished', 'blob': NamedBlobFile(data='foo')})

        browser.open(
            self.meeting,
            view='poll_meeting_zip?job_id={}'.format(zip_job.job_id),
            method='POST')
        self.assertEqual(1, browser.json['zipped'], browser.json)

    @browsing
    def test_zip_polling_view_reports_skipped(self, browser):
        self.login(self.meeting_user, browser)

        job_manager = ZipJobManager(self.meeting.model)
        zip_job = job_manager.create_job()
        zip_job.add_doc_status(IUUID(self.document), {'status': 'skipped'})

        browser.open(
            self.meeting,
            view='poll_meeting_zip?job_id={}'.format(zip_job.job_id),
            method='POST')
        self.assertEqual(1, browser.json['skipped'])


class TestDownloadMeetingZip(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    @browsing
    def test_download_meeting_zip(self, browser):
        self.login(self.meeting_user, browser)

        exporter = MeetingZipExporter(self.meeting.model)
        exporter.zip_job = exporter.job_manager.create_job()
        exporter.zip_job.add_doc_status(
            IUUID(self.document), {'status': 'converting'})

        doc_in_job_id = exporter.zip_job._get_doc_in_job_id(self.document)
        exporter.receive_pdf(doc_in_job_id,
                             'application/pdf',
                             'i am a apdf.')
        exporter.generate_zipfile()

        browser.open(
            self.meeting,
            view='download_meeting_zip?job_id={}'.format(exporter.zip_job.job_id))
        self.assertEquals('application/zip', browser.contenttype)

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertEquals(
            ['meeting.json'],
            zip_file.namelist())

    @browsing
    def test_exported_meeting_json_has_correct_file_names(self, browser):
        set_preferred_language(self.portal.REQUEST, 'de-ch')
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.committee_responsible, browser)

        docs = []

        self.meeting.model.title = u'9. Sitzung der Rechnungspr\xfcfungs' \
                                   u'kommission, ordentlich'
        self.schedule_paragraph(self.meeting, u'A Gesch\xfcfte')
        with freeze(localized_datetime(2017, 12, 13)):
            ad_hoc_agenda_item = self.schedule_ad_hoc(
                self.meeting, u'Ad-hoc Traktand\xfem'
            )
            ad_hoc_agenda_item.decide()
            docs.append(ad_hoc_agenda_item.resolve_document())

        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)

        proposal = agenda_item.proposal.resolve_submitted_proposal()
        docs.append(proposal.get_proposal_document())
        docs.append(proposal.get_excerpt())
        docs.extend(proposal.get_documents())

        with freeze(localized_datetime(2017, 12, 14)):
            docs.append(self.generate_agenda_item_list(self.meeting))
            self.meeting.model.close()

        docs.append(self.meeting.model.protocol_document.resolve_document())

        # fake pdf conversion, make sure files for the ZIP are available
        exporter = MeetingZipExporter(self.meeting.model)
        exporter.zip_job = exporter.job_manager.create_job()
        for doc in docs:
            exporter.zip_job.add_doc_status(IUUID(doc), {'status': 'converting'})
            doc_in_job_id = exporter.zip_job._get_doc_in_job_id(doc)
            exporter.receive_pdf(doc_in_job_id, 'application/pdf', 'apdf.')
        exporter.generate_zipfile()

        browser.open(
            self.meeting,
            view='download_meeting_zip?job_id={}'.format(exporter.zip_job.job_id))
        self.assertEquals('application/zip', browser.contenttype)

        zip_file = ZipFile(StringIO(browser.contents), 'r')

        meeting_json = json.loads(zip_file.read('meeting.json'))

        # the protocol and agenda_item_list are generated during the tests and
        # their checksums cannot be predicted
        meeting_json['meetings'][0]['protocol']['checksum'] = 'unpredictable'
        meeting_json['meetings'][0]['documents'][0]['checksum'] = 'unpredictable'
        meeting_json['meetings'][0].pop('opengever_id')
        for agenda_item in meeting_json['meetings'][0]['agenda_items']:
            agenda_item.pop('opengever_id')

        expected_meeting_json = {
            u'meetings': [{
                u'agenda_items': [
                    {u'sort_order': 1, u'title': u'A Gesch\xfcfte'},
                    {
                        u'number': u'1.',
                        u'number_raw': 1,
                        u'proposal': {
                            u'checksum': u'e00d6c8fb32c30d3ca3a3f8e5d873565482567561023016d9ca18243ff1cfa14',
                            u'file': u'Traktandum 1/Ad-hoc Traktandthm.pdf',
                            u'modified': u'2017-12-13T00:00:00+01:00',
                        },
                        u'sort_order': 2,
                        u'title': u'Ad-hoc Traktand\xfem',
                    },
                    {
                        u'attachments': [{
                            u'checksum': u'51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
                            u'file': u'Traktandum 2/Beilage/1_Vertraegsentwurf.pdf',
                            u'modified': u'2016-08-31T16:09:33+02:00',
                            u'title': u'Vertr\xe4gsentwurf',
                        }],
                        u'number': u'2.',
                        u'number_raw': 2,
                        u'proposal': {
                            u'checksum': u'114e7a059dc34c7459dab90904685584e331089d80bb6310183a0de009b66c3b',
                            u'file': u'Traktandum 2/Vertraege.pdf',
                            u'modified': u'2016-08-31T16:09:33+02:00',
                        },
                        u'sort_order': 3,
                        u'title': u'Vertr\xe4ge',
                    },
                ],
                u'committee': {u'oguid': u'plone:1010073300', u'title': u'Rechnungspr\xfcfungskommission'},
                u'end': u'2016-09-12T17:00:00+00:00',
                u'location': u'B\xfcren an der Aare',
                u'protocol': {
                    u'checksum': 'unpredictable',
                    u'file': u'Protokoll-9. Sitzung der Rechnungspruefungskommission- ordentlich.pdf',
                    u'modified': u'2017-12-14T00:00:00+01:00',
                },
                u'documents': [{
                    u'checksum': 'unpredictable',
                    u'file': u'Traktandenliste-9. Sitzung der Rechnungspruefungskommission- ordentlich.pdf',
                    u'modified': u'2017-12-14T00:00:00+01:00',
                    u'title': u'Traktandenliste-9. Sitzung der Rechnungspr\xfcfungskommission, ordentlich',
                }],
                u'start': u'2016-09-12T15:30:00+00:00',
                u'title': u'9. Sitzung der Rechnungspr\xfcfungskommission, ordentlich',
            }],
            u'version': u'1.0.0',
        }
        self.assert_json_structure_equal(expected_meeting_json, meeting_json)

        expected_file_names = [
            'Protokoll-9. Sitzung der Rechnungspruefungskommission- ordentlich.pdf',
            'Traktandenliste-9. Sitzung der Rechnungspruefungskommission- ordentlich.pdf',
            'Traktandum 1/Ad-hoc Traktandthm.pdf',
            'Traktandum 2/Beilage/1_Vertraegsentwurf.pdf',
            'Traktandum 2/Vertraege.pdf',
            'meeting.json',
            ]
        file_names = sorted(zip_file.namelist())
        self.assertEqual(expected_file_names, file_names)
