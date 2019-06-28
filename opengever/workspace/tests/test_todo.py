from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase


class TestToDo(IntegrationTestCase):

    def test_todo_have_auto_increment_ids(self):
        self.login(self.administrator)
        todo = create(Builder('todo').within(self.workspace)
                      .titled(u'The Todo'))
        self.assertEquals('/plone/workspaces/workspace-1/todo-1',
                          '/'.join(todo.getPhysicalPath()))

        todo = create(Builder('todo').within(self.workspace)
                      .titled(u'Another todo'))
        self.assertEquals('/plone/workspaces/workspace-1/todo-2',
                          '/'.join(todo.getPhysicalPath()))
