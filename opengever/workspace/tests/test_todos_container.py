from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase


class TestTodosContainer(IntegrationTestCase):

    def test_can_be_added(self):
        self.login(self.administrator)
        container = create(Builder('todos container').within(self.workspace))
        self.assertEquals('/plone/workspaces/workspace-1/todos',
                          '/'.join(container.getPhysicalPath()))
