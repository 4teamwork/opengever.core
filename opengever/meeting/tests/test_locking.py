from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import ILockable
from plone.protect import createToken


class TestMeetingLocking(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeetingLocking, self).setUp()
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
            pre_protocol_template=self.sablon_template,
            protocol_template=self.sablon_template,
            excerpt_template=self.sablon_template))

        self.committee = create(Builder('committee').within(container))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .having(title='Mach doch',
                                       committee=self.committee.load_model())
                               .as_submitted())

        self.committee_model = self.committee.load_model()
        self.meeting = create(Builder('meeting')
                              .having(title="My meeting",
                                      committee=self.committee_model,
                                      location='Somewhere')
                              .link_with(self.meeting_dossier))
        self.proposal_model = self.proposal.load_model()

        self.agenda_item = create(
            Builder('agenda_item')
            .having(meeting=self.meeting,
                    proposal=self.proposal_model))

    @browsing
    def test_editing_a_protocol_locks_meeting(self, browser):
        browser.login().open(self.meeting.get_url(view='protocol'))

        browser.open(self.meeting.get_url(view='plone_lock_info/lock_info'))
        lock_infos = ILockable(
            MeetingWrapper.wrap(self.committee, self.meeting)).lock_info()

        self.assertEquals(1, len(lock_infos))
        lock = lock_infos[0]
        self.assertEquals('Meeting:1', lock.get('token'))
        self.assertEquals(TEST_USER_ID, lock.get('creator'))

    @browsing
    def test_lock_refreshing_is_enabled(self, browser):
        browser.login().open(self.meeting.get_url(view='protocol'))
        self.assertIn('enableUnlockProtection', browser.css('#form').first.get('class'))

    @browsing
    def test_saving_protocol_unlock_meeting(self, browser):
        browser.login().open(self.meeting.get_url(view='protocol'))
        lock_infos = ILockable(
            MeetingWrapper.wrap(self.committee, self.meeting)).lock_info()
        self.assertEquals(1, len(lock_infos))

        browser.find('Save').click()
        self.assertEquals(
            [], ILockable(
                MeetingWrapper.wrap(self.committee, self.meeting)).lock_info())

    @browsing
    def test_cancelling_protocol_unlock_meeting(self, browser):
        browser.login().open(self.meeting.get_url(view='protocol'))
        lock_infos = ILockable(
            MeetingWrapper.wrap(self.committee, self.meeting)).lock_info()
        self.assertEquals(1, len(lock_infos))

        browser.find('Close').click()
        self.assertEquals(
            [], ILockable(
                MeetingWrapper.wrap(self.committee, self.meeting)).lock_info())

    @browsing
    def test_protocol_raise_redirect_back_to_meeting_view_when_protocol_is_locked(self, browser):
        user = create(Builder('user')
                      .named('Hugo', 'Boss')
                      .in_groups('client1_users'))
        browser.login(username='hugo.boss').open(self.meeting.get_url(view='protocol'))

        browser.login().open(self.meeting.get_url(view='protocol'))

        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1',
            browser.url,
            'Expected redirect')

    @browsing
    def test_meeting_view_shows_information_when_is_locked(self, browser):
        user = create(Builder('user')
                      .named('Hugo', 'Boss')
                      .in_groups('client1_users'))
        browser.login(username='hugo.boss').open(self.meeting.get_url(view='protocol'))

        browser.login().open(self.meeting.get_url(),
                             {'_authenticator': createToken()})

        # the unlock link is rendered as a submit button, therefore `unlock`
        # is missing in the following statement
        self.assertEquals(
            ['This item was locked by Boss Hugo 1 minute ago. If you are '
             'certain this user has abandoned the object, you may the object. '
             'You will then be able to edit it.'],
            info_messages())
