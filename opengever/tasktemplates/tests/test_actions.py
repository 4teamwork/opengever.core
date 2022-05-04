from opengever.base.interfaces import IContextActions
from opengever.testing import IntegrationTestCase
from zope.component import queryMultiAdapter


class TestTaskTemplateContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_task_template_folder_context_actions(self):
        self.login(self.administrator)
        expected_actions = [u'delete', u'edit']
        self.assertEqual(expected_actions, self.get_actions(self.tasktemplatefolder))

    def test_task_template_context_actions(self):
        self.login(self.administrator)
        expected_actions = [u'delete', u'edit']
        self.assertEqual(expected_actions, self.get_actions(self.tasktemplate))
