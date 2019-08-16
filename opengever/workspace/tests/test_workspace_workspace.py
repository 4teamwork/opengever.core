from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase
from zope.component import getUtility
import json


class TestWorkspaceWorkspace(IntegrationTestCase):

    @browsing
    def test_workspace_is_addable_in_workspaceroot(self, browser):
        self.login(self.workspace_owner, browser)
        browser.visit(self.workspace_root)
        factoriesmenu.add('Workspace')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': 'Example Workspace'})
        form.save()

        assert_no_error_messages(browser)
        workspace = browser.context

        self.assertEquals((('gunther.frohlich', ('WorkspaceOwner',)),),
                          workspace.get_local_roles())
        self.assertEquals(
            [{'cause': ASSIGNMENT_VIA_SHARING,
              'roles': ['WorkspaceOwner'],
              'reference': None,
              'principal': 'gunther.frohlich'}],
            RoleAssignmentManager(workspace).storage._storage())

    @browsing
    def test_workspace_folder_is_addable_in_workspace(self, browser):
        self.login(self.workspace_owner, browser)
        browser.visit(self.workspace)
        factoriesmenu.add('WorkspaceFolder')

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
                    and 'WorkspaceFolder' in factoriesmenu.addable_types()

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
                    and 'ToDo' in factoriesmenu.addable_types()

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


class TestWorkspaceWorkspaceAPI(IntegrationTestCase):

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
