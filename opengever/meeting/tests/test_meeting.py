from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from opengever.meeting.wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase
from pyquery import PyQuery


class TestMeeting(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeeting, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repo = create(Builder('repository_root'))
        self.repository_folder = create(Builder('repository')
                                        .within(self.repo))
        self.templates = create(Builder('templatefolder'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))
        self.sablon_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))
        self.container = create(Builder('committee_container').having(
                                protocol_template=self.sablon_template,
                                excerpt_template=self.sablon_template))
        self.committee = create(Builder('committee')
                                .within(self.container)
                                .link_with(self.repository_folder))
        self.committee_model = self.committee.load_model()
        self.peter = create(Builder('member')
                            .having(firstname=u'Peter', lastname=u'M\xfcller'))
        self.membership = create(Builder('membership')
                                 .having(committee=self.committee_model,
                                         member=self.peter))

    def test_meeting_title(self):
        self.assertEqual(
            u'My Title',
            Meeting(title="My Title").get_title())

    def test_meeting_link(self):
        meeting = create(Builder('meeting').having(
            committee=self.committee.load_model()))

        link = PyQuery(meeting.get_link())[0]

        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view',
            link.get('href'))
        self.assertEqual('contenttype-opengever-meeting-meeting', link.get('class'))
        self.assertEqual(u'C\xf6mmunity meeting', link.get('title'))
        self.assertEqual(u'C\xf6mmunity meeting', link.text)

    @browsing
    def test_regression_add_meeting_without_end_date_does_not_fail(self, browser):
        # create meeting
        browser.login().open(self.committee, view='add-meeting')
        browser.fill({
            'Start': '01.01.2010 10:00',
            'End': '',
            'Location': u'B\xe4rn',
        }).submit()
        # create dossier
        browser.find('Save').click()

        committee_model = self.committee.load_model()
        self.assertEqual(1, len(committee_model.meetings))
        meeting = committee_model.meetings[0]
        self.assertIsNone(meeting.end)

    @browsing
    def test_add_meeting_and_dossier(self, browser):
        # create meeting
        browser.login().open(self.committee, view='add-meeting')
        browser.fill({
            'Start': '01.01.2010 10:00',
            'End': '01.01.2010 11:00',
            'Location': 'Somewhere',
        }).submit()

        # create dossier
        self.assertEqual(u'Meeting on Jan 01, 2010',
                         browser.find('Title').value)
        browser.find('Save').click()

        # back to meeting page
        self.assertEqual(
            [u'The meeting and its dossier were created successfully'],
            info_messages())
        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1#meetings',
            browser.url)

        committee_model = self.committee.load_model()
        self.assertEqual(1, len(committee_model.meetings))
        meeting = committee_model.meetings[0]

        self.assertEqual(self.localized_datetime(2010, 1, 1, 10), meeting.start)
        self.assertEqual(self.localized_datetime(2010, 1, 1, 11), meeting.end)
        self.assertEqual('Somewhere', meeting.location)
        self.assertEqual([Member.get(self.peter.member_id)],
                         meeting.participants)
        dossier = meeting.dossier_oguid.resolve_object()
        self.assertIsNotNone(dossier)
        self.assertEquals(u'Meeting on Jan 01, 2010', dossier.title)
        self.assertIsNotNone(meeting.modified)

    @browsing
    def test_close_meeting(self, browser):
        close_meeting_button_name = 'Close meeting'

        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model)
                         .link_with(self.meeting_dossier))
        create(Builder('agenda_item').having(meeting=meeting,
                                             title='Mach ize'))
        create(Builder('agenda_item').having(meeting=meeting,
                                             title='Oebbis in revision',
                                             workflow_state='revision'))

        # CommitteeResponsible is assigned globally here for the sake of
        # simplicity
        self.grant('Contributor', 'Editor', 'Reader', 'MeetingUser',
                   'CommitteeResponsible')

        browser.login().open(meeting.get_url())
        browser.find(close_meeting_button_name).click()

        meeting = Meeting.query.get(meeting.meeting_id)
        self.assertEqual('closed', meeting.workflow_state)
        self.assertEqual(1, meeting.agenda_items[0].decision_number)
        self.assertEqual(1, meeting.meeting_number)

        # javascript redirects upon close, we need to do so manually here ...
        browser.open(meeting.get_url())
        self.assertEqual(
            [u'The meeting C\xf6mmunity meeting has been successfully '
             u'closed, the excerpts have been generated and sent back to the '
             u'initial dossier.'],
            info_messages())
        self.assertIsNone(browser.find(close_meeting_button_name))

    def test_reopen_transition_not_available(self):
        """Meetings can only be reopened when the word-feature is enabled.
        """
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model,
                                 workflow_state='closed'))
        self.assertEquals(
            [],
            [transition.name for transition
             in meeting.workflow.get_transitions(meeting.get_state())
             if meeting.workflow.can_execute_transition(meeting, transition.name)])


class TestCommitteeMemberVocabulary(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestCommitteeMemberVocabulary, self).setUp()

        self.admin_unit.public_url = 'http://nohost/plone'

        self.repo = create(Builder('repository_root'))
        self.repository_folder = create(Builder('repository')
                                        .within(self.repo))

        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .within(self.container)
                                .link_with(self.repository_folder))

        self.committee_model = self.committee.load_model()

        self.meeting = create(Builder('meeting').having(
            committee=self.committee_model))

        self.wrapper = MeetingWrapper(self.committee, self.meeting)

    def test_return_member_as_value(self):
        member = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))

        create(Builder('membership').having(
            committee=self.committee_model,
            member=member))

        vocabulary = get_committee_member_vocabulary(
            MeetingWrapper(self.committee, self.meeting))

        self.assertEqual(
            member,
            vocabulary._terms[0].value)

    def test_return_fullname_as_title(self):
        member = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))

        create(Builder('membership').having(
            committee=self.committee_model,
            member=member))

        vocabulary = get_committee_member_vocabulary(
            MeetingWrapper(self.committee, self.meeting))

        self.assertEqual(
            u'M\xfcller Hans',
            vocabulary._terms[0].title)

    def test_return_fullname_with_email_as_value(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'M\xfcller',
            email=u'mueller@example.com'))

        create(Builder('membership').having(
            committee=self.committee_model,
            member=member))

        vocabulary = get_committee_member_vocabulary(
            MeetingWrapper(self.committee, self.meeting))

        self.assertEqual(
            u'M\xfcller Hans (mueller@example.com)',
            vocabulary._terms[0].title)
