from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestAttendeesPresenceStatesPatch(IntegrationTestCase):

    @browsing
    def test_patch_attendees_presence_states(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, method='PATCH', headers=self.api_headers,
                     data=json.dumps({'attendees': [self.workspace_guest.id,
                                                    self.workspace_admin.id,
                                                    self.workspace_owner.id]}))

        browser.open(self.workspace_meeting, method='GET', headers=self.api_headers)
        self.assertEqual({self.workspace_admin.id: u'present',
                          self.workspace_guest.id: u'present',
                          self.workspace_owner.id: u'present'},
                         browser.json['attendees_presence_states'])

        browser.open(self.workspace_meeting, view='@attendees-presence-states', method='PATCH',
                     headers=self.api_headers, data=json.dumps(
                         {self.workspace_owner.id: u'absent', self.workspace_admin.id: u'excused'}))
        self.assertEqual(204, browser.status_code)

        browser.open(self.workspace_meeting, method='GET', headers=self.api_headers)
        self.assertEqual({self.workspace_admin.id: u'excused',
                          self.workspace_guest.id: u'present',
                          self.workspace_owner.id: u'absent'},
                         browser.json['attendees_presence_states'])

    @browsing
    def test_cannot_patch_state_of_user_who_is_not_an_attendee(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, method='PATCH', headers=self.api_headers,
                     data=json.dumps({'attendees': [self.workspace_guest.id,
                                                    self.workspace_owner.id]}))

        with browser.expect_http_error(400):
            browser.open(self.workspace_meeting, view='@attendees-presence-states',
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps({self.workspace_admin.id: u'excused'}))

        self.assertEqual({u'type': u'BadRequest', u'additional_metadata': {},
                          u'translated_message': u'User with userid fridolin.hugentobler '
                                                 u'is not a participant in this meeting.',
                          u'message': u'userid_not_in_attendees'}, browser.json)

    @browsing
    def test_cannot_patch_invalid_presence_state_raises_bad_request(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, method='PATCH', headers=self.api_headers,
                     data=json.dumps({'attendees': [self.workspace_guest.id,
                                                    self.workspace_owner.id]}))

        with browser.expect_http_error(400):
            browser.open(self.workspace_meeting, view='@attendees-presence-states',
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps({self.workspace_guest.id: u'too late'}))

        self.assertEqual({u'type': u'BadRequest', u'additional_metadata': {},
                          u'translated_message': u'State too late does not exist.',
                          u'message': u'invalid_presence_state'}, browser.json)
