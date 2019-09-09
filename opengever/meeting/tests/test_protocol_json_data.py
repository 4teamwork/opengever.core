from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.meeting.browser.sablontemplate import SAMPLE_MEETING_DATA
from opengever.meeting.interfaces import IMeetingSettings
from opengever.meeting.protocol import ExcerptProtocolData
from opengever.meeting.protocol import ProtocolData
from opengever.testing import FunctionalTestCase
from plone import api
import copy


class TestProtocolJsonData(FunctionalTestCase):

    maxDiff = None

    def setUp(self):
        super(TestProtocolJsonData, self).setUp()
        self.root = create(Builder('repository_root'))
        self.folder = create(Builder('repository').titled('Strafwesen'))
        self.dossier = create(
            Builder("dossier").within(self.folder))
        self.doc1 = create(Builder("document")
                           .titled(u'Beweisaufn\xe4hme')
                           .within(self.dossier)
                           .attach_file_containing("lorem ipsum",
                                                   name=u"beweisaufnahme.docx"))
        self.doc2 = create(Builder("document")
                           .titled(u"Strafbefehl")
                           .within(self.dossier))
        self.mail1 = create(Builder("mail")
                            .titled(u"L\xf6rem")
                            .with_message("lorem", filename=u"lorem.eml")
                            .within(self.dossier))
        self.committee = create(Builder('committee')
                                .with_default_period()
                                .having(title=u'Gemeinderat'))
        self.proposal = create(
            Builder('proposal')
            .within(self.dossier)
            .having(committee=self.committee,
                    title=u'Strafbefehl wegen Bauens ohne Bewilligung',
                    description=u'Bau Beschreibung',
                    dossier_reference_number=u'FD 2.6.8/1',
                    repository_folder_title=u'Strafwesen')
            .relate_to(self.doc1, self.doc2, self.mail1)
            .as_submitted()
            .from_template(self.doc1))
        self.proposal_model = self.proposal.load_model()
        self.submitted_proposal = self.proposal_model.resolve_submitted_proposal()
        self.member_peter = create(Builder('member'))
        self.member_franz = create(Builder('member')
                                   .having(firstname=u'Franz',
                                           lastname=u'M\xfcller',
                                           email="mueller@example.com"))
        self.member_anna = create(Builder('member')
                                  .having(firstname=u'Anna',
                                          lastname=u'B\xe4nni',
                                          email="baenni@example.com"))
        self.member_otto = create(Builder('member')
                                  .having(firstname=u'Otto',
                                          lastname=u'G\xfcnter',
                                          email="guenter@example.com"))
        self.membership_peter = create(Builder('membership').having(
            member=self.member_peter,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=u'F\xfcrst'))
        self.membership_franz = create(Builder('membership').having(
            member=self.member_franz,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=None))
        self.membership_anna = create(Builder('membership').having(
            member=self.member_anna,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=None))
        self.membership_otto = create(Builder('membership').having(
            member=self.member_otto,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role='Moderator'))
        self.committee_secretary = create(
            Builder('ogds_user')
            .id('committee.secretary')
            .having(firstname=u'C\xf6mmittee', lastname='Secretary', email='committee.secretary@example.com')
            )
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            participants=[self.member_peter,
                          self.member_franz,
                          self.member_anna],
            other_participants=u'Hans M\xfcller\nHeidi Muster',
            protocol_start_page_number=42,
            meeting_number=11,
            presidency=self.member_peter,
            secretary=self.committee_secretary,))

        self.agend_item_text = create(
            Builder('agenda_item').having(
                title=u'R\xfccktritt Hans Muster',
                description=u'R\xfccktritt Grund',
                meeting=self.meeting,
                decision_number=2,))

        self.agenda_item_proposal = create(
            Builder('agenda_item').having(
                proposal=self.proposal_model,
                meeting=self.meeting,
                decision_number=1))

    def test_protocol_json(self):
        with freeze(datetime(2018, 5, 4)):
            data = ProtocolData(self.meeting).get_processed_data()
        expected_data = copy.deepcopy(SAMPLE_MEETING_DATA)
        expected_data.update({'document': {'generated': '04.05.2018'}})
        expected_data['meeting']['date'] = '13.12.2011'
        self.assertDictEqual(expected_data, data)

    def test_date_formatting_string_affects_protocol_json(self):
        api.portal.set_registry_record("sablon_date_format_string", u'%Y %m %d', interface=IMeetingSettings)
        with freeze(datetime(2018, 5, 4)):
            data = ProtocolData(self.meeting).get_processed_data()
        expected_data = copy.deepcopy(SAMPLE_MEETING_DATA)
        expected_data.update({'document': {'generated': '2018 05 04'}})
        expected_data['meeting']['date'] = '2011 12 13'
        self.assertDictEqual(expected_data, data)

    def test_get_attending_members_handles_participants_are_no_longer_committee_memberships(self):
        create_session().delete(self.membership_anna)

        self.assertEquals(
            [{'firstname': 'Anna',
              'lastname': u'B\xe4nni',
              'fullname': u'B\xe4nni Anna',
              'email': 'baenni@example.com',
             'role': None},
             {'email': u'mueller@example.com',
              'firstname': u'Franz',
              'fullname': u'M\xfcller Franz',
              'lastname': u'M\xfcller',
              'role': None},
             ],
            ProtocolData(self.meeting).get_attending_members())


class TestExcerptJsonData(FunctionalTestCase):

    maxDiff = None

    def setUp(self):
        super(TestExcerptJsonData, self).setUp()
        self.proposal = create(
            Builder('proposal_model'))
        self.committee = create(Builder('committee_model')
                                .having(title=u'Gemeinderat'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            protocol_start_page_number=13,
            meeting_number=11,))

    def test_excerpt_json_does_not_contain_start_page(self):
        with freeze(datetime(2018, 5, 4)):
            data = ExcerptProtocolData(self.meeting).get_processed_data()

        self.assertEqual({
            'agenda_items': [],
            'protocol': {'type': u'Protocol-Excerpt'},
            'document': {'generated': u'04.05.2018'},
            'participants': {'other': [], 'members': [], 'absentees': []},
            'committee': {'name': u'Gemeinderat'},
            'mandant': {'name': u'Admin Unit 1'},
            'meeting': {'date': u'13.12.2011',
                        'start_time': u'09:30 AM',
                        'end_time': u'11:45 AM',
                        'number': 11,
                        'location': u'B\xe4rn',
                        }},
            data
        )
