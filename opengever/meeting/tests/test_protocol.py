from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.z3cform import erroneous_fields
from opengever.base.model import create_session
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.locking.lock import SYS_LOCK
from opengever.locking.model import Lock
from opengever.meeting.browser.protocol import GenerateProtocol
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.testing import FunctionalTestCase
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import STEALABLE_LOCK
import transaction


class TestProtocol(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestProtocol, self).setUp()

        # CommitteeResponsible is assigned globally here for the sake of
        # simplicity
        self.grant('Contributor', 'Editor', 'Reader', 'MeetingUser',
                   'CommitteeAdministrator', 'CommitteeResponsible')

        self.admin_unit.public_url = 'http://nohost/plone'

        self.repository_root, self.repository_folder = create(
            Builder('repository_tree'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))

        self.templates = create(Builder('templatefolder'))
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
        self.proposal, self.submitted_proposal = create(
            Builder('proposal')
            .within(self.dossier)
            .having(title='Mach doch',
                    committee=self.committee.load_model())
            .with_submitted())

        self.committee_model = self.committee.load_model()
        self.meeting = create(Builder('meeting')
                              .having(title='My meeting',
                                      committee=self.committee_model,
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

        # This redirect is done through javascript
        browser.open(self.meeting.get_url())

    def setup_generated_protocol(self, browser):
        self.setup_protocol(browser)
        browser.css('.generate-protocol').first.click()

    def test_default_protocol_is_configured_on_commitee_container(self):
        self.assertEqual(self.sablon_template,
                         self.committee.get_protocol_template())

    @browsing
    def test_protocol_template_can_be_configured_per_commitee(self, browser):
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

        browser.find('Protocol-My meeting').click()
        document = browser.context
        lockable = ILockable(document)

        self.assertTrue(lockable.locked())
        self.assertTrue(lockable.can_safely_unlock(SYS_LOCK))
        self.assertFalse(lockable.can_safely_unlock(STEALABLE_LOCK))

        lock_info = lockable.lock_info()[0]
        self.assertEqual(u'sys.lock', lock_info['type'].__name__)

    @browsing
    def test_special_message_for_locked_generated_protocols(self, browser):
        self.setup_generated_protocol(browser)

        browser.find('Protocol-My meeting').click()

        self.assertEqual(
            ['This protocol will remain locked until the meeting My meeting is closed.'],
            info_messages(),
            "There should be a special locking message for a locked generated "
            "protocol"
            )

        self.assertEqual(
            self.meeting.get_url(),
            browser.css('.portalMessage.info a').first.get('href'),
            "The message should contain a link to the related meeting object."
            )

    @browsing
    def test_protocol_document_is_unlocked_when_meeting_is_closed(self, browser):
        self.setup_generated_protocol(browser)

        browser.find('Close meeting').click()

        browser.open(self.meeting.get_url())

        browser.find('Protocol-My meeting').click()
        document = browser.context
        lockable = ILockable(document)

        self.assertFalse(lockable.locked())

    @browsing
    def test_protocol_is_generated_when_closing_meetings(self, browser):
        self.setup_protocol(browser)

        self.assertFalse(self.meeting.has_protocol_document())

        browser.find('Close meeting').click()

        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertTrue(meeting.has_protocol_document())

    @browsing
    def test_protocol_shows_validation_errors(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))
        browser.fill({'Protocol start-page': 'uhoh, no int'}).submit()

        self.assertEqual(['There were some errors.'], error_messages())
        self.assertIn('Protocol start-page',
                      erroneous_fields(browser.forms['form']))

    @browsing
    def test_renders_correct_fields_for_free_text_agenda_item(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model,
                                 start=self.localized_datetime(2014, 1, 1, 10, 45),
                                 location='Somewhere',
                                 protocol_start_page_number=11)
                         .link_with(self.meeting_dossier))
        create(Builder('agenda_item').having(meeting=meeting))

        browser.login()
        browser.open(meeting.get_url(view='protocol'))

        self.assertEqual(
            ['Discussion', 'Decision'],
            browser.css('.agenda_items .item label').text
        )

    @browsing
    def test_renders_correct_fields_for_proposal_based_agenda_item(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))
        self.assertEqual(
            ['Legal basis', 'Initial position', 'Proposed action',
             'Considerations', 'Discussion', 'Decision', 'Publish in',
             'Disclose to', 'Copy for attention'],
            browser.css('.agenda_items .item label').text
        )

    @browsing
    def test_does_not_render_any_field_for_paragraph(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model,
                                 start=self.localized_datetime(2014, 1, 1, 10, 45),
                                 location='Somewhere',
                                 protocol_start_page_number=11)
                         .link_with(self.meeting_dossier))
        create(Builder('agenda_item').having(meeting=meeting, is_paragraph=True))

        browser.login()
        browser.open(meeting.get_url(view='protocol'))

        self.assertEqual([], browser.css('.agenda_items .item label').text)

    @browsing
    def test_protocol_fields_are_xss_safe(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))
        browser.fill({
            'Legal basis':
            '<div onload="alert(\'qux\');">Hans<script>alert("qux");</script></div>'
        }).submit()

        self.assertEqual('<div>Hans</div>',
                         self.submitted_proposal.legal_basis)

    @browsing
    def test_protocol_can_be_edited_and_strips_whitespace(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))
        self.assertIsNotNone(self.meeting.modified)
        prev_modified = self.meeting.modified

        browser.fill({'Title': 'The Meeting',
                      'Legal basis': '<div>Yes we can</div>',
                      'Initial position': '<div>Still the same</div>',
                      'Considerations': '<div>It is important</div>',
                      'Proposed action': '<div>Accept it</div>',
                      'Discussion': '<div>We should accept it</div>',
                      'Decision': '<div>Accepted</div>',
                      'Publish in': '<div> <br> \n &nbsp;there&nbsp; <br /> \t </div>',
                      'Disclose to': '<div>&nbsp;    </div>',
                      'Copy for attention': '<div>Hanspeter</div>',
                      'Protocol start-page': '10'}).submit()
        self.assertEqual({
            u'redirectUrl': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view'},
            browser.json)
        browser.open(self.meeting.get_url(view='view'))
        self.assertEqual(['Changes saved'], info_messages())

        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertGreater(meeting.modified, prev_modified)
        self.assertEqual('The Meeting', meeting.title)

        self.assertEqual('<div>Yes we can</div>',
                         self.submitted_proposal.legal_basis)
        self.assertEqual('<div>Still the same</div>',
                         self.submitted_proposal.initial_position)
        self.assertEqual('<div>It is important</div>',
                         self.submitted_proposal.considerations)
        self.assertEqual('<div>Accept it</div>',
                         self.submitted_proposal.proposed_action)
        self.assertEqual('<div>there</div>',
                         self.submitted_proposal.publish_in)
        self.assertEqual('<div></div>',
                         self.submitted_proposal.disclose_to)
        self.assertEqual('<div>Hanspeter</div>',
                         self.submitted_proposal.copy_for_attention)

        agenda_item = AgendaItem.get(self.agenda_item.agenda_item_id)
        self.assertEqual('<div>We should accept it</div>', agenda_item.discussion)
        self.assertEqual('<div>Accepted</div>', agenda_item.decision)

        # This redirect is done through javascript
        browser.open(self.meeting.get_url())

        self.assertEqual(self.meeting.get_url(), browser.url)

    @browsing
    def test_protocol_participants_can_be_edited(self, browser):
        peter = create(Builder('member'))
        create(Builder('membership').having(
            member=peter,
            committee=self.committee_model))
        prev_modified = self.meeting.modified

        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))

        browser.fill({'Presidency': str(peter.member_id),
                      'Participants': str(peter.member_id),
                      'Other Participants': 'Klara'}).submit()

        self.assertEqual({
            u'redirectUrl': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view'},
            browser.json)
        browser.open(self.meeting.get_url(view='view'))
        self.assertEqual(['Changes saved'], info_messages())

        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertGreater(meeting.modified, prev_modified)

        # refresh intances
        meeting = Meeting.query.get(self.meeting.meeting_id)
        peter = Member.get(peter.member_id)

        self.assertSequenceEqual([peter], meeting.participants)
        self.assertEqual(peter, meeting.presidency)
        self.assertEqual(u'Klara', meeting.other_participants)

    @browsing
    def test_protocol_conflicts_are_detected(self, browser):
        browser.login()
        browser.open(self.meeting.get_url(view='protocol'))

        browser.fill({"modified": '1'}).submit()
        self.assertEqual({u'hasConflict': True}, browser.json)

    @browsing
    def test_protocol_cannot_be_saved_when_locked_by_another_user(self, browser):
        browser.login()
        # acquire the lock for test-user
        browser.open(self.meeting.get_url(view='protocol'))

        # simulate somebody stealing the lock in the meantime
        sess = create_session()
        lock = sess.query(Lock).one()
        lock.creator = 'another.user'
        transaction.commit()

        # the form is still open and can be submitted, but fails
        browser.fill({'Legal basis': u'Yes we can'}).submit()
        self.assertEqual({
            u'messages': [{
                u'messageTitle': u'Error',
                u'message': u'Your changes were not saved, the protocol is locked by another.user.',
                u'messageClass': u'error'}
            ]},
            browser.json
        )

    @browsing
    def test_protocol_can_be_downloaded(self, browser):
        self.setup_protocol(browser)
        browser.css('.generate-protocol').first.click()

        meeting = Meeting.query.first()
        expected_data = meeting.protocol_document.resolve_document().file.data

        browser.css('a.download-protocol-btn').first.click()
        self.assertEqual(browser.headers['content-type'], MIME_DOCX)
        self.assertEqual(expected_data, browser.contents)

    @browsing
    def test_protocol_can_be_generated(self, browser):
        self.setup_protocol(browser)
        browser.css('a[href*="@@generate_protocol"]').first.click()

        self.assertEquals(
            ['Protocol for meeting My meeting '
             'has been generated successfully.'],
            info_messages())

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        self.assertIsNotNone(meeting.protocol_document)
        generated_document = meeting.protocol_document
        self.assertIsNotNone(generated_document)
        self.assertEqual(0, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)

    @browsing
    def test_generating_protocol_twice_displays_error_message(self, browser):
        self.setup_protocol(browser)
        browser.open(GenerateProtocol.url_for(self.meeting))

        browser.open(GenerateProtocol.url_for(self.meeting))
        self.assertEqual('The protocol for meeting My meeting has already '
                         'been generated.', error_messages()[0])

    @browsing
    def test_generated_protocol_can_be_updated(self, browser):
        self.setup_generated_protocol(browser)

        browser.open(self.meeting.get_url())
        browser.css('a[href*="@@update_protocol"]').first.click()

        meeting = Meeting.get(self.meeting.meeting_id)  # refresh meeting
        generated_document = meeting.protocol_document

        self.assertIsNotNone(generated_document)
        self.assertEqual(1, generated_document.generated_version)
        self.assertEqual(meeting, generated_document.meeting)
        self.assertEqual(1, GeneratedProtocol.query.count())

    @browsing
    def test_protocol_displays_numbers_in_navigation(self, browser):
        self.setup_protocol(browser)

        create(Builder('agenda_item').having(meeting=self.meeting,
                                             title='Mach ize'))

        browser.open(self.meeting.get_url())
        browser.css('a[href*="/protocol"]').first.click()

        navigation = browser.css('.navigation > ul > li > a')
        headings = browser.css('.protocol_title .title .text')
        numbers = browser.css('.protocol_title .number')

        self.assertEqual(map(lambda nav: nav.text, navigation),
                         ['1. Mach ize', '2. Mach doch'])
        self.assertEqual(map(lambda heading: heading.text, headings),
                         ['Mach ize', 'Mach doch'])

        self.assertEqual(map(lambda number: number.text, numbers),
                         ['1.', '2.'])

    @browsing
    def test_decided_agenda_items_will_not_be_loaded_in_editor(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model,
                                 start=self.localized_datetime(2014, 1, 1, 10, 45),
                                 location='Somewhere',
                                 protocol_start_page_number=11)
                         .link_with(self.meeting_dossier))
        agenda_item = create(Builder('agenda_item')
                             .having(meeting=meeting,
                                     discussion="My talks",
                                     decision=""
                                     ))

        agenda_item.decide()

        browser.login()
        browser.open(meeting.get_url(view='protocol'))

        self.assertEqual(
            ['My talks'],
            browser.css('.readonly').text,
            'The attributes should not be loaded in the editor because '
            'the agenda_item was decided.')

    @browsing
    def test_not_decided_agenda_items_will_be_loaded_in_editor(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model,
                                 start=self.localized_datetime(2014, 1, 1, 10, 45),
                                 location='Somewhere',
                                 protocol_start_page_number=11)
                         .link_with(self.meeting_dossier))
        create(Builder('agenda_item').having(meeting=meeting))

        browser.login()
        browser.open(meeting.get_url(view='protocol'))

        self.assertEqual(
            ['Discussion', 'Decision'],
            browser.css('.agenda_items .item label').text
        )

        self.assertEqual(
            2, len(browser.css('.trix-input')),
            'Each field should be loaded with the trix editor because '
            'the agenda_item is not decided yet')


class TestFormatParticipant(FunctionalTestCase):

    def test_return_fullname_if_no_email(self):
        member = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))

        self.assertEqual(u'M\xfcller Hans', member.get_title())

    def test_return_fullname_with_email(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'M\xfcller',
            email=u'hans.mueller@example.com'))

        self.assertEqual(
            u'M\xfcller Hans (<a href="mailto:hans.mueller@example.com">hans.mueller@example.com</a>)',
            member.get_title())

    def test_return_fullname_without_linked_email(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'M\xfcller',
            email=u'hans.mueller@example.com'))

        self.assertEqual(
            u'M\xfcller Hans (hans.mueller@example.com)',
            member.get_title(show_email_as_link=False))

    def test_result_is_html_escaped(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'<script></script>M\xfcller'))

        self.assertEqual(
            u'&lt;script&gt;&lt;/script&gt;M\xfcller Hans',
            member.get_title())
