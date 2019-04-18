from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.testing import IntegrationTestCase
from zope.component import getUtility


class TestWorkspaceFolder(IntegrationTestCase):

    @browsing
    def test_workspacefolder_is_addable_in_workspacefolder(self, browser):
        self.login(self.workspace_member, browser)
        browser.visit(self.workspace_folder)
        factoriesmenu.add('WorkspaceFolder')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Ein Unter\xf6rdnerli'})
        form.save()

        assert_no_error_messages(browser)

    def test_sequence_number(self):
        self.login(self.workspace_guest)
        self.assertEquals(
            1, getUtility(ISequenceNumber).get_number(self.workspace_folder))

    def test_workspace_generated_ids(self):
        self.login(self.workspace_guest)
        self.assertEquals('folder-1', self.workspace_folder.getId())

    @browsing
    def test_security_view_access(self, browser):
        for user in (self.workspace_owner,
                     self.workspace_admin,
                     self.workspace_member,
                     self.workspace_guest):
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace_folder)
                assert_no_error_messages()

    @browsing
    def test_security_edit_action(self, browser):
        expected = {self.workspace_owner: True,
                    self.workspace_admin: True,
                    self.workspace_member: True,
                    self.workspace_guest: False}

        got = {}
        for user in expected.keys():
            locals()['__traceback_info__'] = user
            with self.login(user, browser):
                browser.open(self.workspace_folder)
                got[user] = editbar.visible() and 'Edit' in editbar.contentviews()

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
                browser.open(self.workspace_folder)
                got[user] = factoriesmenu.visible() \
                            and 'Document' in factoriesmenu.addable_types()

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
                browser.open(self.workspace_folder)
                got[user] = factoriesmenu.visible() \
                            and 'WorkspaceFolder' in factoriesmenu.addable_types()

        self.assertEquals(expected, got)
