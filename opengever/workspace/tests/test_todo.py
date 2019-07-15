from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase


class TestToDo(IntegrationTestCase):

    @browsing
    def test_todo_is_addable_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        browser.visit(self.workspace)
        factoriesmenu.add('ToDo')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Ein ToDo'})
        form.save()

        assert_no_error_messages(browser)

    def test_searchable_text(self):
        self.login(self.workspace_admin)
        self.assertItemsEqual(
            ['fix', 'user', 'login', 'authentication', 'is', 'no', 'longer', 'possible'],
            index_data_for(self.todo).get('SearchableText'))
