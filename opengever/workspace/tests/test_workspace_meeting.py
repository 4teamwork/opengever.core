from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.testing import IntegrationTestCase
import json


class TestWorkspaceMeeting(IntegrationTestCase):

    @browsing
    def test_workspace_meeting_is_addable_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        browser.visit(self.workspace)
        with self.observe_children(self.workspace) as children:
            factoriesmenu.add('Workspace Meeting')
            browser.fill({'Title': u'Ein Meeting',
                          'Start': '10.10.2020 23:56'})
            form = browser.find_form_by_field('Organizer')
            form.find_widget('Organizer').fill(self.workspace_member.getId(), auto_org_unit=False)
            browser.click_on('Save')

        assert_no_error_messages(browser)
        self.assertEqual(1, len(children['added']))
        meeting = children['added'].pop()
        self.assertEqual(meeting.Title(), u'Ein Meeting')


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
    def test_workspace_meeting_can_have_attendees(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, method='POST', headers=self.api_headers,
            data=json.dumps({'title': 'Ein Meeting',
                             'responsible': self.workspace_member.getId(),
                             'attendees': [self.workspace_guest.getId(), self.workspace_admin.getId()],
                             'start': '2020-10-10T23:56:00',
                             '@type': 'opengever.workspace.meeting'}))

        self.assertEqual(
            [
                {u'token': u'hans.peter', u'title': u'Peter Hans'},
                {u'token': u'fridolin.hugentobler', u'title': u'Hugentobler Fridolin'}
            ], browser.json.get('attendees'))

    @browsing
    def test_only_actual_workspace_members_can_participate_to_a_meeting_workspace_meeting(self, browser):
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
