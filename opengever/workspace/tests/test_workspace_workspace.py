from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.testing import IntegrationTestCase
from zope.component import getUtility


class TestWorkspaceWorkspace(IntegrationTestCase):

    @browsing
    def test_workspace_is_addable_in_workspaceroot(self, browser):
        self.login(self.manager, browser)
        browser.visit(self.workspace_root)
        factoriesmenu.add('Workspace')

        form = browser.find_form_by_field('Title')
        form.find_widget('Responsible').fill(self.regular_user.getId())
        form.fill({'Title': 'Example Workspace'})
        form.save()

        assert_no_error_messages(browser)

    def test_sequence_number(self):
        self.assertEquals(
            1, getUtility(ISequenceNumber).get_number(self.workspace))

    def test_workspace_generated_ids(self):
        self.assertEquals('workspace-1', self.workspace.getId())
