from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.testing import IntegrationTestCase


class TestToDoList(IntegrationTestCase):

    @browsing
    def test_todolist_is_addable_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        browser.visit(self.workspace)
        factoriesmenu.add('ToDo list')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Projekteinf\xfchrung'})
        form.save()

        assert_no_error_messages(browser)
