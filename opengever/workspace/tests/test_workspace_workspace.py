from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.browser import edit_public_trial
from opengever.base.interfaces import ISequenceNumber
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.component import getUtility


class TestWorkspaceWorkspace(IntegrationTestCase):

    @browsing
    def test_workspace_is_addable_in_workspaceroot(self, browser):
        self.login(self.workspace_owner, browser)
        browser.visit(self.workspace_root)
        factoriesmenu.add('Workspace')

        form = browser.find_form_by_field('Title')
        form.find_widget('Responsible').fill(self.regular_user.getId())
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
    def test_workspace_overview_subdossierstructure(self, browser):
        self.login(self.workspace_owner, browser=browser)
        browser.visit(self.workspace, view='dossier_navigation.json')
        self.assertEquals([{u'description': u'',
                            u'nodes': [],
                            u'text': u'',
                            u'uid': IUUID(self.workspace_folder),
                            u'url': self.workspace_folder.absolute_url()}],
                          browser.json[0]['nodes'])

    def test_can_access_public_trial_edit_form_for_files_in_workspace(self):
        self.login(self.workspace_owner)

        document = create(Builder('document').within(self.workspace))
        self.assertTrue(edit_public_trial.can_access_public_trial_edit_form(self.workspace_owner, document))
        self.assertTrue(edit_public_trial.can_access_public_trial_edit_form(self.workspace_admin, document))
        self.assertFalse(edit_public_trial.can_access_public_trial_edit_form(self.workspace_member, document))
        self.assertFalse(edit_public_trial.can_access_public_trial_edit_form(self.workspace_guest, document))
