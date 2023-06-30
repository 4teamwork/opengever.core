from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase
from opengever.workspace.workspace import FOOTER_DEFAULT_FORMAT
from zope.component import getUtility
import json


class TestWorkspaceWorkspace(IntegrationTestCase):

    @browsing
    def test_workspace_is_addable_in_workspaceroot(self, browser):
        self.login(self.workspace_admin, browser)
        browser.visit(self.workspace_root)
        factoriesmenu.add('Workspace')

        browser.exception_bubbling = True
        form = browser.find_form_by_field('Title')
        form.fill({'Title': 'Example Workspace'})
        form.save()

        assert_no_error_messages(browser)
        workspace = browser.context

        self.assertEquals((('fridolin.hugentobler', ('WorkspaceAdmin',)),),
                          workspace.get_local_roles())
        self.assertEquals(
            [{'cause': ASSIGNMENT_VIA_SHARING,
              'roles': ['WorkspaceAdmin'],
              'reference': None,
              'principal': 'fridolin.hugentobler'}],
            RoleAssignmentManager(workspace).storage._storage())
        self.assertIsNotNone(
            workspace.videoconferencing_url)
        self.assertIn(
             u'https://meet.jit.si/', workspace.videoconferencing_url)

    @browsing
    def test_workspace_folder_is_addable_in_workspace(self, browser):
        self.login(self.workspace_owner, browser)
        browser.visit(self.workspace)
        factoriesmenu.add('Workspace Folder')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': 'Example Folder'})
        form.save()

        assert_no_error_messages(browser)
        folder = browser.context

        self.assertEquals(u'Example Folder', folder.title)

    def test_sequence_number(self):
        self.login(self.workspace_member)
        self.assertEquals(
            1, getUtility(ISequenceNumber).get_number(self.workspace))

    def test_workspace_generated_ids(self):
        self.login(self.workspace_member)
        self.assertEquals('workspace-1', self.workspace.getId())

    def test_default_addable_types(self):
        self.login(self.workspace_member)
        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.workspace.todo',
             'opengever.workspace.todolist',
             'opengever.workspace.folder',
             'opengever.workspace.meeting'],
            [fti.id for fti in self.workspace.allowedContentTypes()])

    def test_addable_types_with_todo_feature_disabled(self):
        self.deactivate_feature('workspace-todo')
        self.login(self.workspace_member)
        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.workspace.folder',
             'opengever.workspace.meeting'],
            [fti.id for fti in self.workspace.allowedContentTypes()])

    def test_addable_types_with_workspace_meeting_feature_disabled(self):
        self.deactivate_feature('workspace-meeting')
        self.login(self.workspace_member)
        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.workspace.folder',
             'opengever.workspace.todo',
             'opengever.workspace.todolist'],
            [fti.id for fti in self.workspace.allowedContentTypes()])

    @browsing
    def test_workspace_creator_is_set_as_responsible_after_creation(self, browser):
        self.login(self.workspace_admin, browser)

        browser.open(self.workspace_root, method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'@type': 'opengever.workspace.workspace',
                                      'title': u'\xfcberarbeitungsphase'}))

        self.assertEqual(201, browser.status_code)
        self.assertEqual({u'token': u'fridolin.hugentobler',
                          u'title': u'Hugentobler Fridolin (fridolin.hugentobler)'},
                         browser.json['responsible'])

    @browsing
    def test_only_workspace_members_are_valid_as_responsibles(self, browser):
        self.login(self.workspace_admin, browser)

        querysource_url = '{}/@querysources/responsible?query=Peter'.format(
            self.workspace.absolute_url())

        browser.open(querysource_url, method='GET', headers=self.api_headers)
        self.assertEqual([{u'title': u'Peter Hans (hans.peter)', u'token': u'hans.peter'}],
                         browser.json['items'])

        # delete workspace_guest
        url = '{}/@participations/{}'.format(
            self.workspace.absolute_url(), self.workspace_guest.id)
        browser.open(url, method='DELETE', headers=self.api_headers)

        browser.open(querysource_url, method='GET', headers=self.api_headers)
        self.assertEqual([], browser.json['items'])

    @browsing
    def test_header_and_footer_configuration_placeholders_are_validated(self, browser):
        self.login(self.workspace_admin, browser)

        footer = dict(FOOTER_DEFAULT_FORMAT)
        browser.open(self.workspace_root, method='POST',
                     headers=self.api_headers,
                     data=json.dumps(
                         {'@type': 'opengever.workspace.workspace',
                          'title': u'\xfcberarbeitungsphase',
                          'meeting_template_footer': footer}))

        footer['center'] = '{print_date} and {invalid_placeholder}'
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.workspace_root, method='POST',
                         headers=self.api_headers,
                         data=json.dumps(
                             {'@type': 'opengever.workspace.workspace',
                              'title': u'\xfcberarbeitungsphase',
                              'meeting_template_header': footer}))

        self.assertEqual(
            u'Invalid meeting minutes configuration, not supported '
            'placeholders "invalid_placeholder" are used.',
            browser.json['translated_message'])

    @browsing
    def test_security_view_access(self, browser):
        for user in (self.workspace_owner,
                     self.workspace_admin,
                     self.workspace_member,
                     self.workspace_guest):
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace)
                assert_no_error_messages()

    @browsing
    def test_security_edit_workspace_action(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: False,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace)
                got[user] = editbar.visible() and 'Edit' in editbar.contentviews()

        self.maxDiff = None
        self.assertEquals(expected, got)

    @browsing
    def test_security_add_documents(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace)
                got[user] = factoriesmenu.visible() \
                    and 'Document' in factoriesmenu.addable_types()

        self.maxDiff = None
        self.assertEquals(expected, got)

    @browsing
    def test_security_add_workspace_folders(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace)
                got[user] = factoriesmenu.visible() \
                    and 'Workspace Folder' in factoriesmenu.addable_types()

        self.assertDictEqual(expected, got)

    @browsing
    def test_security_add_workspace_meetings(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace)
                got[user] = factoriesmenu.visible() \
                    and 'Workspace Meeting' in factoriesmenu.addable_types()

        self.assertDictEqual(expected, got)

    @browsing
    def test_security_edit_workspace_meeting_action(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace_meeting)
                got[user] = editbar.visible() and 'Edit' in editbar.contentviews()

        self.maxDiff = None
        self.assertEquals(expected, got)

    @browsing
    def test_security_add_workspace_meetings(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace)
                got[user] = factoriesmenu.visible() \
                    and 'Workspace Meeting' in factoriesmenu.addable_types()

        self.maxDiff = None
        self.assertEquals(expected, got)

    @browsing
    def test_security_add_todos(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace)
                got[user] = factoriesmenu.visible() \
                    and 'To-do item' in factoriesmenu.addable_types()

        self.maxDiff = None
        self.assertEquals(expected, got)

    @browsing
    def test_security_edit_todo_action(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.todo)
                got[user] = editbar.visible() and 'Edit' in editbar.contentviews()

        self.maxDiff = None
        self.assertEquals(expected, got)

    def test_access_members_allowed_for_guests_if_flag_disabled(self):
        self.login(self.workspace_admin)
        self.workspace.hide_members_for_guests = False

        self.login(self.workspace_guest)
        self.assertTrue(self.workspace.access_members_allowed())

    def test_access_members_disallowed_for_guests_if_flag_enabled(self):
        self.login(self.workspace_admin)
        self.workspace.hide_members_for_guests = True

        self.login(self.workspace_guest)
        self.assertFalse(self.workspace.access_members_allowed())

    def test_access_members_allowed_for_members_and_admins(self):
        self.login(self.workspace_admin)
        self.workspace.hide_members_for_guests = True

        self.assertTrue(self.workspace.access_members_allowed())

        self.login(self.workspace_member)
        self.assertTrue(self.workspace.access_members_allowed())


class TestWorkspaceWorkspaceAPI(IntegrationTestCase):

    EXPECTED_ADD_INVITATION_ACTION = {
        u'title': u'Add invitation',
        u'id': u'add_invitation',
        u'icon': u''
    }

    @browsing
    def test_update(self, browser):
        self.login(self.workspace_owner, browser)

        browser.open(self.workspace, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xfcberarbeitungsphase'}))

        self.assertEqual(204, browser.status_code)
        self.assertEqual(u'\xfcberarbeitungsphase',
                         self.workspace.title)

    @browsing
    def test_update_as_member_is_not_allowed(self, browser):
        self.login(self.workspace_member, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.workspace, method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'title': u'\xfcberarbeitungsphase'}))

    @browsing
    def test_workspace_admin_can_view_add_invitation_action(self, browser):
        self.login(self.workspace_admin, browser)

        browser.open(self.workspace, view='@actions', headers=self.api_headers)
        actions = browser.json['object_buttons']

        self.assertIn(self.EXPECTED_ADD_INVITATION_ACTION, actions)

    @browsing
    def test_workspace_admin_cannot_see_add_invitation_action_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.set_workflow_state('opengever_workspace--STATUS--inactive', self.workspace)

        browser.open(self.workspace, view='@actions', headers=self.api_headers)
        actions = browser.json['object_buttons']

        self.assertNotIn(self.EXPECTED_ADD_INVITATION_ACTION, actions)

    @browsing
    def test_workspace_member_cannot_see_add_invitation_action(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(self.workspace, view='@actions', headers=self.api_headers)
        actions = browser.json['object_buttons']

        self.assertNotIn(self.EXPECTED_ADD_INVITATION_ACTION, actions)
