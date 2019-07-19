from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
import json


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


class TestAPISupportForTodo(IntegrationTestCase):

    @browsing
    def test_create(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, method='POST', headers=self.api_headers,
            data=json.dumps({'title': 'Ein ToDo',
                             '@type': 'opengever.workspace.todo'}))

        self.assertEqual(201, browser.status_code)
        self.assertEqual('Ein ToDo',
                         browser.json['title'])
        self.assertEqual('todo-4', browser.json['id'])

    @browsing
    def test_read(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.todo, method='GET', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(u'Fix user login', browser.json['title'])
        self.assertEqual(u'opengever.workspace.todo', browser.json['@type'])
        self.assertEqual(u'opengever_workspace_todo--STATUS--active',
                         browser.json['review_state'])

    @browsing
    def test_update(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xc4 new login'}))

        self.assertEqual(204, browser.status_code)
        self.assertEqual(u'\xc4 new login', self.todo.title)

    @browsing
    def test_deletion_is_only_possible_for_managers(self, browser):
        self.login(self.workspace_member, browser)
        with browser.expect_http_error(401):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

        self.login(self.workspace_admin, browser)
        with browser.expect_http_error(401):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

        self.login(self.workspace_owner, browser)
        with browser.expect_http_error(401):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

        self.login(self.manager, browser)
        todo_id = self.todo.id
        browser.open(self.todo, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(todo_id, self.workspace.objectIds())
