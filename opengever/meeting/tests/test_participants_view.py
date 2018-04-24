from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestParticipantsView(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_change_role(self, browser):
        self.login(self.committee_responsible, browser)
        meeting = self.meeting.model
        member = self.committee_participant_1.model
        self.assertNotEqual(member, meeting.presidency)

        browser.open(self.meeting, view='participants/change_role',
                     data={'member_id': member.member_id,
                           'role': 'presidency'})
        self.assertEqual({u'proceed': True}, browser.json)
        self.assertEqual(member, meeting.presidency)

        browser.open(self.meeting, view='participants/change_role',
                     data={'member_id': member.member_id,
                           'role': ''})
        self.assertEqual({u'proceed': True}, browser.json)
        self.assertIsNone(meeting.presidency)

    @browsing
    def test_secretary_not_rendered_in_dropdown_menu(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertNotIn('Secretary', browser.css('select.role').text)

    @browsing
    def test_meeting_user_cannot_change_role(self, browser):
        self.login(self.meeting_user, browser)
        member = self.committee_participant_1.model
        browser.open(self.meeting, view='participants/change_role',
                     data={'member_id': member.member_id,
                           'role': 'presidency'})
        self.assertEqual(
            {u'messages': [{u'message': u'You are not allowed to change'
                            ' the meeting details.',
                            u'messageClass': u'error',
                            u'messageTitle': u'Error'}],
             u'proceed': False},
            browser.json)

    @browsing
    def test_change_presence(self, browser):
        self.login(self.committee_responsible, browser)
        meeting = self.meeting.model
        member = self.committee_participant_2.model
        self.assertIn(member, meeting.participants)

        browser.open(self.meeting, view='participants/change_presence',
                     data={'member_id': member.member_id,
                           'present': json.dumps(False)})
        self.assertEqual({u'proceed': True}, browser.json)
        self.assertNotIn(member, meeting.participants)

        browser.open(self.meeting, view='participants/change_presence',
                     data={'member_id': member.member_id,
                           'present': json.dumps(True)})
        self.assertEqual({u'proceed': True}, browser.json)
        self.assertIn(member, meeting.participants)

    @browsing
    def test_meeting_user_cannot_change_presence(self, browser):
        self.login(self.meeting_user, browser)
        member = self.committee_participant_1.model
        browser.open(self.meeting, view='participants/change_presence',
                     data={'member_id': member.member_id,
                           'present': json.dumps(True)})
        self.assertEqual(
            {u'messages': [{u'message': u'You are not allowed to change'
                            ' the meeting details.',
                            u'messageClass': u'error',
                            u'messageTitle': u'Error'}],
             u'proceed': False},
            browser.json)
