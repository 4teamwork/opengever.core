from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.z3cform import erroneous_fields
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.locking.lock import SYS_LOCK
from opengever.meeting.browser.protocol import METHOD_NEW_DOCUMENT
from opengever.meeting.browser.protocol import METHOD_NEW_VERSION
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.model import Proposal
from opengever.testing import FunctionalTestCase
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import STEALABLE_LOCK


class TestProtocol(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestProtocol, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repository_root, self.repository_folder = create(
            Builder('repository_tree'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))

        self.templates = create(Builder('templatedossier'))
        self.sablon_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))
        container = create(Builder('committee_container').having(
            protocol_template=self.sablon_template,
            excerpt_template=self.sablon_template))

        self.committee = create(
            Builder('committee')
            .within(container)
            .having(repository_folder=self.repository_folder))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .having(title='Mach doch',
                                       committee=self.committee.load_model())
                               .as_submitted())

        self.committee_model = self.committee.load_model()
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee_model,
                                      start=self.localized_datetime(2013, 1, 1, 10, 45),
                                      location='There',
                                      protocol_start_page_number=42)
                              .link_with(self.meeting_dossier))
        self.proposal_model = self.proposal.load_model()

        self.agenda_item = create(
            Builder('agenda_item')
            .having(meeting=self.meeting,
                    proposal=self.proposal_model))
        self.proposal_model.execute_transition('submitted-scheduled')

    def setup_protocol(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))
        browser.fill({'Considerations': 'It is important',
                      'Proposed action': 'Accept it',
                      'Discussion': 'We should accept it',
                      'Decision': 'Accepted'}).submit()

    def setup_generated_protocol(self, browser):
        self.setup_protocol(browser)
        browser.css('a[href*="@@generate_protocol"]').first.click()

    def test_default_protocol_is_configured_on_commitee_container(self):
        self.assertEqual(self.sablon_template,
                         self.committee.get_protocol_template())

    @browsing
    def test_protocol_template_can_be_configured_per_commitee(self, browser):
        self.grant("Administrator")
        custom_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))

        browser.login().open(self.committee, view='edit')
        browser.fill({'Protocol template': custom_template})
        browser.css('#form-buttons-save').first.click()
        self.assertEqual([], error_messages())

        self.assertEqual(custom_template,
                         self.committee.get_protocol_template())

    @browsing
    def test_protocol_document_is_locked_by_system_once_generated(self, browser):
        self.setup_generated_protocol(browser)

        browser.find('Protocol-there-jan-01-2013').click()
        document = browser.context
        lockable = ILockable(document)

        self.assertTrue(lockable.locked())
        self.assertTrue(lockable.can_safely_unlock(SYS_LOCK))
        self.assertFalse(lockable.can_safely_unlock(STEALABLE_LOCK))

        lock_info = lockable.lock_info()[0]
        self.assertEqual(u'sys.lock', lock_info['type'].__name__)

    @browsing
    def test_protocol_document_is_unlocked_when_meeting_is_closed(self, browser):
        self.setup_generated_protocol(browser)
        browser.find('Close meeting').click()

        browser.find('Protocol-there-jan-01-2013').click()
        document = browser.context
        lockable = ILockable(document)

        self.assertFalse(lockable.locked())

    @browsing
    def test_protocol_shows_validation_errors(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))
        browser.fill({'Protocol start-page': 'uhoh, no int'}).submit()

        self.assertEqual(['There were some errors.'], error_messages())
        self.assertIn('Protocol start-page',
                      erroneous_fields(browser.forms['form']))

    @browsing
    def test_protocol_can_be_edited(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))

        browser.fill({'Legal basis': 'Yes we can',
                      'Initial position': 'Still the same',
                      'Considerations': 'It is important',
                      'Proposed action': 'Accept it',
                      'Discussion': 'We should accept it',
                      'Decision': 'Accepted',
                      'Publish in': 'There',
                      'Disclose to': 'Nobody',
                      'Copy for attention': 'Hanspeter',
                      'Protocol start-page': '10'}).submit()

        self.assertEquals(['Changes saved'], info_messages())

        proposal = Proposal.query.get(self.proposal_model.proposal_id)
        self.assertEqual('Yes we can', proposal.legal_basis)
        self.assertEqual('Still the same', proposal.initial_position)
        self.assertEqual('It is important', proposal.considerations)
        self.assertEqual('Accept it', proposal.proposed_action)
        self.assertEqual('There', proposal.publish_in)
        self.assertEqual('Nobody', proposal.disclose_to)
        self.assertEqual('Hanspeter', proposal.copy_for_attention)

        agenda_item = AgendaItem.get(self.agenda_item.agenda_item_id)
        self.assertEqual('We should accept it', agenda_item.discussion)
        self.assertEqual('Accepted', agenda_item.decision)

        self.assertEqual(self.meeting.get_url(), browser.url)

    @browsing
    def test_protocol_participants_can_be_edited(self, browser):
        peter = create(Builder('member'))
        hans = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))
        create(Builder('membership').having(
            member=peter,
            committee=self.committee_model).as_active())
        create(Builder('membership').having(
            member=hans,
            committee=self.committee_model).as_active())

        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))

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
    def test_protocol_can_be_downloaded(self, browser):
        self.setup_protocol(browser)
        browser.css('.generate-protocol').first.click()
        browser.css('a[href$="download_protocol"]').first.click()
        self.assertEqual(browser.headers['content-type'], MIME_DOCX)
        self.assertIsNotNone(browser.contents)

    @browsing
    def test_protocol_can_be_generated(self, browser):
        self.setup_protocol(browser)
        browser.css('a[href*="@@generate_protocol"]').first.click()

        self.assertEquals(
            ['Protocol for meeting There, Jan 01, 2013 '
             'has been generated successfully'],
            info_messages())

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        self.assertIsNotNone(meeting.protocol_document)
        generated_document = meeting.protocol_document
        self.assertIsNotNone(generated_document)
        self.assertEqual(0, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)

    @browsing
    def test_generated_protocol_can_be_updated(self, browser):
        self.setup_generated_protocol(browser)

        browser.open(self.meeting.get_url())
        browser.css('a[href*="@@update_protocol"]').first.click()
        browser.fill({'form.widgets.method': METHOD_NEW_VERSION}).submit()

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        document = browser.context
        generated_document = GeneratedProtocol.query.by_document(
            document).first()
        self.assertIsNotNone(generated_document)
        self.assertEqual(1, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)
        self.assertEqual(1, GeneratedProtocol.query.count())

    @browsing
    def test_new_generated_protocol_can_be_created(self, browser):
        self.setup_generated_protocol(browser)

        browser.open(self.meeting.get_url())
        browser.css('a[href*="@@update_protocol"]').first.click()
        browser.fill({'form.widgets.method': METHOD_NEW_DOCUMENT}).submit()

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        document = browser.context
        generated_document = GeneratedProtocol.query.by_document(
            document).first()
        self.assertIsNotNone(generated_document)
        self.assertEqual(0, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)
        self.assertEqual(1, GeneratedProtocol.query.count())

    @browsing
    def test_protocol_displays_numbers_in_navigation(self, browser):
        self.setup_protocol(browser)

        create(Builder('agenda_item').having(meeting=self.meeting,
                                             title='Mach ize'))

        browser.open(self.meeting.get_url())
        browser.css('a[href*="/protocol"]').first.click()

        navigation = browser.css('#scrollspy a.expandable')
        headings = browser.css('.protocol_title .title')

        self.assertEqual(map(lambda nav: nav.text, navigation),
                         ['1. Mach doch', '2. Mach ize'])
        self.assertEqual(map(lambda heading: heading.text, headings),
                         ['1. Mach doch', '2. Mach ize'])
