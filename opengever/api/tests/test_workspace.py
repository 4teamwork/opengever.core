from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.workspace.todos.storage import ToDoListStorage
import json


class TestWorkspaceSerializer(IntegrationTestCase):

    @browsing
    def test_workspace_serialization_contains_can_manage_participants(self, browser):
        self.login(self.workspace_member, browser)
        response = browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertFalse(response.get(u'can_manage_participants'))

        self.login(self.workspace_owner, browser)
        response = browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertTrue(response.get(u'can_manage_participants'))


class TestWorkspacePost(IntegrationTestCase):

    @browsing
    def test_added_todo_will_not_be_added_to_a_todo_list_by_default(self, browser):
        self.login(self.workspace_owner, browser)
        storage = ToDoListStorage(self.workspace)

        browser.open(
            self.workspace.absolute_url(),
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                '@type': 'opengever.workspace.todo',
                'title': u'Important todo'}),
        )

        self.assertEqual([], storage.list())

    @browsing
    def test_add_todo_to_a_todo_list(self, browser):
        self.login(self.workspace_owner, browser)
        storage = ToDoListStorage(self.workspace)
        todo_list = storage.create_todo_list('01 - General')

        todo = browser.open(
            self.workspace.absolute_url(),
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                '@type': 'opengever.workspace.todo',
                'title': u'Important todo',
                'todo_list_id': todo_list.get('list_id')}),
        ).json

        self.assertEqual(
            [
                {
                    'todo_uids': [todo.get('UID')],
                    'list_id': todo_list.get('list_id'),
                    'title': '01 - General'
                }
            ], storage.list())
