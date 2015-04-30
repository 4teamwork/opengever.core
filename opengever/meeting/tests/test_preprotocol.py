from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.browser.meetings.protocol import EditPreProtocol
from opengever.meeting.browser.protocol import METHOD_NEW_DOCUMENT
from opengever.meeting.browser.protocol import METHOD_NEW_VERSION
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import GeneratedPreProtocol
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.model import Proposal
from opengever.testing import FunctionalTestCase


class TestPreProtocol(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestPreProtocol, self).setUp()

        self.repository_root = create(Builder('repository_root'))
        self.repository_folder = create(
            Builder('repository').within(self.repository_root))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))

        self.templates = create(Builder('templatedossier'))
        self.sablon_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))
        container = create(Builder('committee_container').having(
            pre_protocol_template=self.sablon_template,
            protocol_template=self.sablon_template,
            excerpt_template=self.sablon_template))

        self.committee = create(Builder('committee').within(container))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .as_submitted()
                               .having(title='Mach doch',
                                       committee=self.committee.load_model()))

        self.committee_model = self.committee.load_model()
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee_model,
                                      start=datetime(2013, 1, 1),
                                      location='There',))
        self.proposal_model = self.proposal.load_model()

        self.agenda_item = create(
            Builder('agenda_item')
            .having(meeting=self.meeting,
                    proposal=self.proposal_model))

    def setup_pre_protocol(self, browser):
        browser.login()
        browser.open(EditPreProtocol.url_for(self.committee, self.meeting))
        browser.fill({'Considerations': 'It is important',
                      'Proposed action': 'Accept it',
                      'Discussion': 'We should accept it',
                      'Decision': 'Accepted'}).submit()

    def setup_generated_pre_protocol(self, browser):
        self.setup_pre_protocol(browser)
        browser.find('Generate').click()
        browser.fill({'Target dossier': self.dossier})
        browser.find('Generate').click()

    def test_default_pre_protocol_is_configured_on_commitee_container(self):
        self.assertEqual(self.sablon_template,
                         self.committee.get_pre_protocol_template())

    @browsing
    def test_pre_protocol_template_can_be_configured_per_commitee(self, browser):
        custom_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))

        browser.login().open(self.committee, view='edit')
        browser.fill({'Pre-protocol template': custom_template})
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(custom_template,
                         self.committee.get_pre_protocol_template())

    @browsing
    def test_pre_protocol_can_be_edited(self, browser):
        browser.login()
        browser.open(EditPreProtocol.url_for(self.committee, self.meeting))

        browser.fill({'Legal basis': 'Yes we can',
                      'Initial position': 'Still the same',
                      'Considerations': 'It is important',
                      'Proposed action': 'Accept it',
                      'Discussion': 'We should accept it',
                      'Decision': 'Accepted'}).submit()

        self.assertEquals(['Changes saved'], info_messages())

        proposal = Proposal.query.get(self.proposal_model.proposal_id)
        self.assertEqual('Yes we can', proposal.legal_basis)
        self.assertEqual('Still the same', proposal.initial_position)
        self.assertEqual('It is important', proposal.considerations)
        self.assertEqual('Accept it', proposal.proposed_action)

        agenda_item = AgendaItem.get(self.agenda_item.agenda_item_id)
        self.assertEqual('We should accept it', agenda_item.discussion)
        self.assertEqual('Accepted', agenda_item.decision)

        self.assertEqual(MeetingList.url_for(self.committee, self.meeting),
                         browser.url)

    @browsing
    def test_pre_protocol_participants_can_be_edited(self, browser):
        peter = create(Builder('member'))
        hans = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))
        create(Builder('membership')
               .having(member=peter, committee=self.committee_model)
               .as_active())
        create(Builder('membership')
               .having(member=hans, committee=self.committee_model)
               .as_active())

        browser.login()
        browser.open(EditPreProtocol.url_for(self.committee, self.meeting))

        browser.fill({'Presidency': str(peter.member_id),
                      'Secretary': str(hans.member_id),
                      'Participants': str(peter.member_id),
                      'Other Participants': 'Klara'}).submit()

        self.assertEquals(['Changes saved'], info_messages())

        # refresh intances
        meeting = Meeting.query.get(self.meeting.meeting_id)
        peter = Member.get(peter.member_id)
        hans = Member.get(hans.member_id)

        self.assertSequenceEqual([peter], meeting.participants)
        self.assertEqual(peter, meeting.presidency)
        self.assertEqual(hans, meeting.secretary)
        self.assertEqual(u'Klara', meeting.other_participants)

    @browsing
    def test_pre_protocol_can_be_downloaded(self, browser):
        self.setup_pre_protocol(browser)
        browser.find('Download preview').click()
        self.assertEqual(browser.headers['content-type'], MIME_DOCX)
        self.assertIsNotNone(browser.contents)

    @browsing
    def test_pre_protocol_can_be_generated(self, browser):
        self.setup_pre_protocol(browser)
        browser.find('Generate').click()
        browser.fill({'Target dossier': self.dossier})
        browser.find('Generate').click()

        self.assertEquals(
            ['Pre-protocol for meeting There, Jan 01, 2013 '
             'has been generated successfully'],
            info_messages())

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        document = browser.context
        generated_document = GeneratedPreProtocol.query.by_document(
            document).first()
        self.assertIsNotNone(generated_document)
        self.assertEqual(0, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)

    @browsing
    def test_generated_pre_protocol_can_be_updated(self, browser):
        self.setup_generated_pre_protocol(browser)

        browser.open(MeetingList.url_for(self.committee, self.meeting))
        browser.find('Generate').click()
        browser.fill({'form.widgets.method:list': METHOD_NEW_VERSION}).submit()

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        document = browser.context
        generated_document = GeneratedPreProtocol.query.by_document(
            document).first()
        self.assertIsNotNone(generated_document)
        self.assertEqual(1, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)
        self.assertEqual(1, GeneratedPreProtocol.query.count())

    @browsing
    def test_new_generated_pre_protocol_can_be_created(self, browser):
        self.setup_generated_pre_protocol(browser)

        browser.open(MeetingList.url_for(self.committee, self.meeting))
        browser.find('Generate').click()
        browser.fill({'form.widgets.method:list': METHOD_NEW_DOCUMENT}).submit()

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        document = browser.context
        generated_document = GeneratedPreProtocol.query.by_document(
            document).first()
        self.assertIsNotNone(generated_document)
        self.assertEqual(0, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)
        self.assertEqual(1, GeneratedPreProtocol.query.count())
