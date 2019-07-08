from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.api.workspace_todos import ToDosGet
from opengever.testing import IntegrationTestCase
from opengever.workspace.todos.storage import ToDoListStorage


class TestWorkspaceToDosGet(IntegrationTestCase):

    @browsing
    def test_do_not_fail_with_empty_workspace(self, browser):
        self.login(self.workspace_owner, browser)
        response = browser.open(
            self.workspace.absolute_url() + '/@todos',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual([], response.get('items'))
        self.assertEqual([], response.get('todo_lists'))

    @browsing
    def test_includes_todos(self, browser):
        self.login(self.workspace_owner, browser)

        todo_1 = create(Builder('todo').within(self.workspace).titled(u'One'))
        todo_2 = create(Builder('todo').within(self.workspace).titled(u'One'))

        response = browser.open(
            self.workspace.absolute_url() + '/@todos',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertItemsEqual([
            todo_1.absolute_url(), todo_2.absolute_url()],
            [item.get('@id') for item in response.get('items')])

    @browsing
    def test_includes_todo_lists(self, browser):
        self.login(self.workspace_owner, browser)

        todo_1 = create(Builder('todo').within(self.workspace).titled(u'One'))
        todo_2 = create(Builder('todo').within(self.workspace).titled(u'One'))

        storage = ToDoListStorage(self.workspace)
        todo_list = storage.create_todo_list('01 - General')
        storage.add_todo_to_list(todo_list.get('list_id'), todo_2.UID())

        response = browser.open(
            self.workspace.absolute_url() + '/@todos',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual([
            {
                u'list_id': todo_list.get('list_id'),
                u'title': u'01 - General',
                u'todo_uids': [todo_2.UID()]
            }
        ], response.get('todo_lists'))

    @browsing
    def test_raise_exception_if_hard_limit_reached(self, browser):
        CURRENT_HARD_LIMIT = ToDosGet.HARD_LIMIT
        ToDosGet.HARD_LIMIT = 1

        self.login(self.workspace_owner, browser)

        create(Builder('todo').within(self.workspace).titled(u'One'))
        create(Builder('todo').within(self.workspace).titled(u'One'))

        try:
            with browser.expect_http_error(500):
                browser.open(
                    self.workspace.absolute_url() + '/@todos',
                    method='GET',
                    headers=self.api_headers,
                )
        finally:
            ToDosGet.HARD_LIMIT = CURRENT_HARD_LIMIT
