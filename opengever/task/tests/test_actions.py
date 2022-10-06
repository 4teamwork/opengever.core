from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from plone import api
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


class TestTaskContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_task_context_actions(self):
        self.login(self.regular_user)
        expected_actions = [u'move_item', u'edit description', u'edit relatedItems']
        self.assertEqual(expected_actions, self.get_actions(self.task))

    def test_edit_action_available_for_task_issuer(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-open', self.task)
        self.assertIn(u'edit', self.get_actions(self.task))

    def test_move_item_action_only_available_if_user_has_move_permission(self):
        self.login(self.regular_user)
        self.assertIn(u'move_item', self.get_actions(self.task))
        self.task.manage_permission('Copy or Move', roles=[])
        self.assertNotIn(u'move_item', self.get_actions(self.task))

    def test_move_item_not_available_for_forwarding(self):
        self.login(self.secretariat_user)
        self.assertTrue(api.user.has_permission('Copy or Move', obj=self.inbox_forwarding))
        self.assertNotIn(u'move_item', self.get_actions(self.inbox_forwarding))

    def test_edit_description_and_related_items_action_available_on_pending_tasks(self):
        self.login(self.regular_user)
        allowed_states = ['task-state-in-progress', 'task-state-open',
                          'task-state-planned', 'task-state-resolved']
        disallowed_states = ['task-state-rejected', 'task-state-tested-and-closed',
                             'task-state-skipped', 'task-state-cancelled']

        for state in allowed_states:
            self.set_workflow_state(state, self.task)
            self.assertIn(u'edit description', self.get_actions(self.task))
            self.assertIn(u'edit relatedItems', self.get_actions(self.task))

        for state in disallowed_states:
            self.set_workflow_state(state, self.task)
            self.assertNotIn(u'edit description', self.get_actions(self.task))
            self.assertNotIn(u'edit relatedItems', self.get_actions(self.task))
