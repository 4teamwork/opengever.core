from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestToDo(IntegrationTestCase):

    def test_todo_have_auto_increment_ids(self):
        self.login(self.administrator)
        container = create(Builder('todos container').within(self.workspace))
        todo = create(Builder('todo').within(container)
                      .titled(u'The Todo'))
        self.assertEquals('/plone/workspaces/workspace-1/todos/1',
                          '/'.join(todo.getPhysicalPath()))

        todo = create(Builder('todo').within(container)
                      .titled(u'Another todo'))
        self.assertEquals('/plone/workspaces/workspace-1/todos/2',
                          '/'.join(todo.getPhysicalPath()))

    @browsing
    def test_create_todo_through_api(self, browser):
        self.login(self.administrator, browser=browser)
        container = create(Builder('todos container').within(self.workspace))
        browser.append_request_header('Accept', 'application/json')
        browser.open(container,
                     method='POST',
                     data=json.dumps({
                         '@type': 'opengever.workspace.todo',
                         'title': 'The firts Todo'}))
        self.assertEquals(['1'], container.objectIds())
