from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from ftw.testing.freezer import freeze
from opengever.testing import IntegrationTestCase
from opengever.workspace.interfaces import IWorkspaceMeetingAttendeesPresenceStateStorage
import json
import pytz


class TestWorkspaceMeeting(IntegrationTestCase):

    @browsing
    def test_workspace_meeting_is_addable_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        browser.visit(self.workspace)
        with self.observe_children(self.workspace) as children:
            factoriesmenu.add('Workspace Meeting')
            browser.fill({'Title': u'Ein Meeting',
                          'Start': '10.10.2020 23:56',
                          'Organizer': self.workspace_member.getId(),
                          'Guests': 'hans muster\ndemo@4teamwork.ch'})
            browser.click_on('Save')

        assert_no_error_messages(browser)
        self.assertEqual(1, len(children['added']))
        meeting = children['added'].pop()
        self.assertEqual(meeting.Title(), u'Ein Meeting')
        self.assertEqual(meeting.guests, ['hans muster', 'demo@4teamwork.ch'])


class TestWorkspaceMeetingWorkflow(IntegrationTestCase):

    def close_workspace_meeting(self, browser):
        browser.open(
            '{}/@workflow/{}'.format(
                self.workspace_meeting.absolute_url(),
                'opengever_workspace_meeting--TRANSITION--close--active_closed',
            ),
            method='POST', headers=self.api_headers,
        )

    def reopen_workspace_meeting(self, browser):
        browser.open(
            '{}/@workflow/{}'.format(
                self.workspace_meeting.absolute_url(),
                'opengever_workspace_meeting--TRANSITION--reopen--closed_active',
            ),
            method='POST', headers=self.api_headers,
        )

    @browsing
    def test_admin_can_close_workspace_meeting(self, browser):
        self.login(self.workspace_admin, browser)
        with freeze(datetime(2020, 9, 4, 10, 30, tzinfo=pytz.UTC)):
            self.close_workspace_meeting(browser)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json,
            {
                u'action': u'opengever_workspace_meeting--TRANSITION--close--active_closed',
                u'actor': u'fridolin.hugentobler',
                u'comments': u'',
                u'review_state': u'opengever_workspace_meeting--STATUS--closed',
                u'time': u'2020-09-04T10:30:00+00:00',
                u'title': u'Closed',
            }
        )

    @browsing
    def test_admin_can_reopen_workspace_meeting(self, browser):
        self.login(self.workspace_admin, browser)
        with freeze(datetime(2020, 9, 4, 10, 30, tzinfo=pytz.UTC)):
            self.close_workspace_meeting(browser)
            self.reopen_workspace_meeting(browser)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json,
            {
                u'action': u'opengever_workspace_meeting--TRANSITION--reopen--closed_active',
                u'actor': u'fridolin.hugentobler',
                u'comments': u'',
                u'review_state': u'opengever_workspace_meeting--STATUS--active',
                u'time': u'2020-09-04T10:30:00+00:00',
                u'title': u'Active',
            }
        )

    @browsing
    def test_member_cannot_reopen_workspace(self, browser):
        self.login(self.workspace_member, browser)
        self.close_workspace_meeting(browser)
        with browser.expect_http_error(400):
            self.reopen_workspace_meeting(browser)
        self.assertEqual(
            browser.json,
            {
                u'error': {
                    u'message': u"Invalid transition "
                                u"'opengever_workspace_meeting--TRANSITION--reopen--closed_active'."
                                u"\nValid transitions are:\n",
                    u'type': u'Bad Request',
                },
            },
        )

    def test_add_modify_and_delete_agendaitem_permission(self):
        workflow = self.portal.portal_workflow['opengever_workspace_meeting']

        self.assertEqual({'acquired': 1, 'roles': []},
                         workflow.states['opengever_workspace_meeting--STATUS--active'
                                         ].getPermissionInfo('Modify portal content'))

        self.assertEqual({'acquired': 0, 'roles': []},
                         workflow.states['opengever_workspace_meeting--STATUS--closed'
                                         ].getPermissionInfo('Modify portal content'))

        self.assertEqual({'acquired': 1, 'roles': []},
                         workflow.states['opengever_workspace_meeting--STATUS--active'
                                         ].getPermissionInfo('Add portal content'))

        self.assertEqual({'acquired': 0, 'roles': []},
                         workflow.states['opengever_workspace_meeting--STATUS--closed'
                                         ].getPermissionInfo('Add portal content'))

        self.assertEqual({'acquired': 1, 'roles': []},
                         workflow.states['opengever_workspace_meeting--STATUS--active'
                                         ].getPermissionInfo(
            'opengever.workspace: Delete Workspace Meeting Agenda Items'))

        self.assertEqual({'acquired': 0, 'roles': []},
                         workflow.states['opengever_workspace_meeting--STATUS--closed'
                                         ].getPermissionInfo(
            'opengever.workspace: Delete Workspace Meeting Agenda Items'))


class TestAPISupportForWorkspaceMeeting(IntegrationTestCase):

    @browsing
    def test_create_workspace_meeting_via_api(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, method='POST', headers=self.api_headers,
            data=json.dumps({'title': 'Ein Meeting',
                             'responsible': self.workspace_member.getId(),
                             'start': '2020-10-10T23:56:00',
                             '@type': 'opengever.workspace.meeting'}))

        self.assertEqual(201, browser.status_code)
        self.assertEqual('Ein Meeting', browser.json['title'])
        self.assertEqual('meeting-2', browser.json['id'])

    @browsing
    def test_create_with_workspace_meeting_feature_disabled(self, browser):
        self.deactivate_feature('workspace-meeting')
        self.login(self.workspace_member, browser)
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'title': 'Ein Meeting',
                                 'responsible': self.workspace_member.getId(),
                                 'start': '2020-10-10T23:56:00',
                                 '@type': 'opengever.workspace.meeting'}))

        self.assertEqual('Disallowed subobject type: opengever.workspace.meeting',
                         browser.json['error']['message'])

    @browsing
    def test_get_workspace_meeting_via_api(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, method='GET', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        expected = {
            u'@id': self.workspace_meeting.absolute_url(),
            u'@type': u'opengever.workspace.meeting',
            u'id': u'meeting-1',
            u'responsible': {u'title': u'Schr\xf6dinger B\xe9atrice',
                             u'token': u'beatrice.schrodinger'},
            u'title': u'Besprechung Kl\xe4ranlage'
        }
        self.assertDictContainsSubset(expected, browser.json)

    @browsing
    def test_update_workspace_meeting_via_api(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xc4 new title'}))

        self.assertEqual(204, browser.status_code)
        self.assertEqual(u'\xc4 new title', self.workspace_meeting.title)

    @browsing
    def test_create_workspace_meeting_with_attendees(self, browser):
        self.login(self.workspace_member, browser)
        with self.observe_children(self.workspace) as children:
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'title': 'Ein Meeting',
                                 'responsible': self.workspace_member.getId(),
                                 'attendees': [self.workspace_guest.getId(),
                                               self.workspace_admin.getId()],
                                 'start': '2020-10-10T23:56:00',
                                 '@type': 'opengever.workspace.meeting'}))

        self.assertEqual(
            [
                {u'token': u'hans.peter', u'title': u'Peter Hans'},
                {u'token': u'fridolin.hugentobler', u'title': u'Hugentobler Fridolin'}
            ], browser.json.get('attendees'))

        meeting = children['added'].pop()
        storage = IWorkspaceMeetingAttendeesPresenceStateStorage(meeting)
        expected_states = {u'hans.peter': u'present', u'fridolin.hugentobler': u'present'}
        self.assertEqual(expected_states, storage.get_all())

        browser.open(meeting, method='GET', headers=self.api_headers)
        self.assertEqual(expected_states, browser.json['attendees_presence_states'])

    @browsing
    def test_presence_states_after_modifying_attendees(self, browser):
        self.login(self.workspace_member, browser)
        storage = IWorkspaceMeetingAttendeesPresenceStateStorage(self.workspace_meeting)
        browser.open(self.workspace_meeting, method='PATCH', headers=self.api_headers,
                     data=json.dumps({'attendees': [
                         self.workspace_guest.getId(), self.workspace_admin.getId()]}))

        storage.add_or_update(self.workspace_guest.getId(), u'excused')
        self.assertEqual({u'hans.peter': u'excused', u'fridolin.hugentobler': u'present'},
                         storage.get_all())

        browser.open(self.workspace_meeting, method='PATCH', headers=self.api_headers,
                     data=json.dumps({'attendees': [
                         self.workspace_member.getId(), self.workspace_guest.getId()]}))

        self.assertEqual({u'hans.peter': u'excused', u'beatrice.schrodinger': u'present'},
                         storage.get_all())

    @browsing
    def test_only_actual_workspace_members_can_participate_to_a_workspace_meeting(self, browser):
        self.login(self.workspace_member, browser)
        with browser.expect_http_error(code=400):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'title': 'Ein Meeting',
                                 'responsible': self.workspace_member.getId(),
                                 'attendees': [self.regular_user.getId()],
                                 'start': '2020-10-10T23:56:00',
                                 '@type': 'opengever.workspace.meeting'}))

        self.assertEqual(
            u"[{'field': 'attendees', "
            "'message': u'Constraint not satisfied', "
            "'error': 'ValidationError'}]",
            browser.json['message'])

    @browsing
    def test_create_workspace_meeting_with_guests(self, browser):
        self.login(self.workspace_member, browser)
        with self.observe_children(self.workspace):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'title': 'Ein Meeting',
                                 'responsible': self.workspace_member.getId(),
                                 'attendees': [self.workspace_guest.getId(),
                                               self.workspace_admin.getId()],
                                 'start': '2020-10-10T23:56:00',
                                 'guests': ['hans muster', 'demo@4teamwork.ch'],
                                 '@type': 'opengever.workspace.meeting'}))

        self.assertEqual([u'hans muster', u'demo@4teamwork.ch'], browser.json.get('guests'))
