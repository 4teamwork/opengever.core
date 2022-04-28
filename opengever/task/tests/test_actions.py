from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from zope.component import queryMultiAdapter


class TestTaskListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='tasks')
        return adapter.get_actions() if adapter else []

    def test_task_actions_for_reporoot_and_repofolder(self):
        self.login(self.regular_user)
        expected_actions = [u'export_tasks', u'pdf_taskslisting']
        self.assertEqual(expected_actions, self.get_actions(self.repository_root))
        self.assertEqual(expected_actions, self.get_actions(self.branch_repofolder))

    def test_task_actions_for_plone_site(self):
        self.login(self.regular_user)
        expected_actions = [u'export_tasks', u'pdf_taskslisting']
        self.assertEqual(expected_actions, self.get_actions(self.portal))

    def test_task_actions_open_for_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'move_items', u'export_tasks', u'pdf_taskslisting']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))
        self.assertEqual(expected_actions, self.get_actions(self.meeting_dossier))

    def test_task_actions_for_closed_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'export_tasks', u'pdf_taskslisting']
        self.assertEqual(expected_actions, self.get_actions(self.expired_dossier))

    def test_task_actions_for_inbox(self):
        self.login(self.secretariat_user)
        expected_actions = [u'export_tasks', u'pdf_taskslisting']
        self.assertEqual(expected_actions, self.get_actions(self.inbox))
