from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.testing import IntegrationTestCase


class TestWorkspaceFolder(IntegrationTestCase):

    @browsing
    def test_workspacefolder_is_addable_in_workspacefolder(self, browser):
        self.login(self.manager, browser)
        browser.visit(self.workspace_folder)
        factoriesmenu.add('WorkspaceFolder')

        form = browser.find_form_by_field('Title')
        form.find_widget('Responsible').fill(self.regular_user.getId())
        form.fill({'Title': 'Example Workspace'})
        form.save()

        assert_no_error_messages(browser)
