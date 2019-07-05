from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.workspace.todos.storage import ToDoListStorage
import json


class TestWorkspaceToDoListPost(IntegrationTestCase):

    @browsing
    def test_adds_a_new_todo_list(self, browser):
        self.login(self.workspace_owner, browser)
        storage = ToDoListStorage(self.workspace)

        self.assertEqual(0, len(storage.list()))

        response = browser.open(
            self.workspace.absolute_url() + '/@todolist',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({'title': u'01 - Gener\xe4l'}),
        ).json

        self.assertEqual(1, len(storage.list()))
        self.assertEqual(u'01 - Gener\xe4l', response.get('title'))
        self.assertEqual([], response.get('todos'))

    @browsing
    def test_raises_when_title_is_missing(self, browser):
        self.login(self.workspace_owner, browser)

        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + '/@todolist',
                method='POST',
                headers=self.api_headers,
                data=json.dumps({'title': u''}),
            )

    @browsing
    def test_adds_a_new_todo_to_a_todo_list(self, browser):
        self.login(self.workspace_owner, browser)
        storage = ToDoListStorage(self.workspace)

        response = browser.open(
            self.workspace.absolute_url() + '/@todolist',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({'title': u'01 - Gener\xe4l'}),
        ).json

        self.assertEqual(
            0,
            len(storage._get_todo_list_by_id(response.get('UID')).todos))

        response = browser.open(
            response.get('@id'),
            method='POST',
            headers=self.api_headers,
            data=json.dumps({'todo_uid': u'123'}),
        ).json

        self.assertEqual(['123'], response.get('todos'))
        self.assertEqual(
            1,
            len(storage._get_todo_list_by_id(response.get('UID')).todos))

    @browsing
    def test_workspace_guest_cannot_add_todo_lists(self, browser):
        self.login(self.workspace_guest, browser)

        with browser.expect_http_error(401):
            browser.open(
                self.workspace.absolute_url() + '/@todolist',
                method='POST',
                headers=self.api_headers,
                data=json.dumps({'title': u'01 - Gener\xe4l'}),
            ).json

    @browsing
    def test_raises_404_if_adding_a_todo_to_a_not_existent_todo_list(self, browser):
        self.login(self.workspace_owner, browser)

        with browser.expect_http_error(404):
            browser.open(
                self.workspace.absolute_url() + '/@todolist/not-existing',
                method='POST',
                headers=self.api_headers,
                data=json.dumps({'todo_uid': u'123'}),
            ).json
