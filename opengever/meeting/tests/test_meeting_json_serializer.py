from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.meeting.zipexport import MeetingDocumentZipper
from opengever.meeting.zipexport import MeetingJSONSerializer
from opengever.testing import IntegrationTestCase
from opengever.testing import set_preferred_language
from opengever.testing.helpers import localized_datetime


class TestMeetingJSONSerializer(IntegrationTestCase):
    features = ('meeting',)
    maxDiff = None

    def test_meeting_data_for_zip_export_json(self):
        set_preferred_language(self.portal.REQUEST, 'de-ch')
        self.login(self.committee_responsible)
        self.schedule_paragraph(self.meeting, u'A Gesch\xfcfte')
        with freeze(localized_datetime(2017, 12, 13)):
            self.schedule_ad_hoc(self.meeting, u'Ad-hoc Traktand\xfem')
        self.schedule_proposal(self.meeting, self.submitted_proposal)

        serializer = MeetingJSONSerializer(
            self.meeting.model,
            MeetingDocumentZipper(self.meeting.model, None))
        serializer.traverse()
        expected_agenda_items = {
            'agenda_items': [
                {'opengever_id': 2, 'sort_order': 1, 'title': u'A Gesch\xfcfte'},
                {
                    'number': '1.', 'number_raw': 1, 'opengever_id': 3, 'proposal': {
                        'checksum': 'e00d6c8fb32c30d3ca3a3f8e5d873565482567561023016d9ca18243ff1cfa14',
                        'file': 'Traktandum 1/Ad-hoc Traktandthm.docx',
                        'modified': u'2017-12-13T00:00:00+01:00',
                    },
                    'sort_order': 2,
                    'title': u'Ad-hoc Traktand\xfem'
                },
                {
                    'attachments': [{
                        'checksum': '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
                        'file': 'Traktandum 2/Beilage/1_Vertraegsentwurf.docx',
                        'modified': u'2016-08-31T16:09:33+02:00',
                        'title': u'Vertr\xe4gsentwurf',
                    }],
                    'number': '2.',
                    'number_raw': 2,
                    'opengever_id': 4,
                    'proposal': {
                        'checksum': '114e7a059dc34c7459dab90904685584e331089d80bb6310183a0de009b66c3b',
                        'file': 'Traktandum 2/Vertraege.docx',
                        'modified': u'2016-08-31T16:09:33+02:00',
                    },
                    'sort_order': 3,
                    'title': u'Vertr\xe4ge',
                },
            ],
            'committee': {'oguid': u'plone:1010073300', 'title': u'Rechnungspr\xfcfungskommission'},
            'end': u'2016-09-12T17:00:00+00:00',
            'location': u'B\xfcren an der Aare',
            'opengever_id': 1,
            'start': u'2016-09-12T15:30:00+00:00',
            'title': u'9. Sitzung der Rechnungspr\xfcfungskommission',
        }

        self.assertEquals(expected_agenda_items, serializer.data)

    def test_filename_conflicts_are_avoided_by_prefixing_attachment_number(self):
        set_preferred_language(self.portal.REQUEST, 'de-ch')
        self.login(self.committee_responsible)

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

        serializer = MeetingJSONSerializer(
            self.meeting.model,
            MeetingDocumentZipper(self.meeting.model, None))
        serializer.traverse()

        expected_file_names = [u'Traktandum 1/Beilage/1_The same title.doc',
                               u'Traktandum 1/Beilage/2_The same title.doc',
                               u'Traktandum 1/Beilage/3_The same title.doc']
        json_file_names = [attachment.get("file") for attachment in
                           serializer.data['agenda_items'][0]["attachments"]]

        self.assertItemsEqual(expected_file_names, json_file_names)
