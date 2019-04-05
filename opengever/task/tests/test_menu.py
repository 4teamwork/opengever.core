from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.task.interfaces import ITaskSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import TEST_USER_ID


class TestFactoryMenu(FunctionalTestCase):

    def setUp(self):
        super(TestFactoryMenu, self).setUp()
        self.menu = FactoriesMenu(self.portal)

    def test_task_menu_item_is_titled_task_in_a_dossier(self):
        dossier = create(Builder('dossier'))

        items = self.menu.getMenuItems(dossier, self.portal.REQUEST)
        task_action = [action for action in items
                       if action.get('id') == 'opengever.task.task'][0]

        self.assertIn(u'Task', task_action.get('title'))

    def test_task_menu_item_is_titled_subtask_inside_a_task(self):
        task = create(Builder('task')
                      .in_progress()
                      .having(title='Task One',
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))

        items = self.menu.getMenuItems(task, self.portal.REQUEST)
        task_action = [action for action in items
                       if action.get('id') == 'opengever.task.task'][0]

        self.assertIn(u'Subtask', task_action.get('title'))
        self.assertEquals(u'icon-task-subtask',
                          task_action.get('extra').get('class'))

    def test_mail_menu_item_is_not_displayed_inside_a_task(self):
        task = create(Builder('task')
                      .in_progress()
                      .having(title='Task One',
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))

        factory_items = [item['id'] for item in
                         self.menu.getMenuItems(task, self.portal.REQUEST)]
        self.assertNotIn('ftw.mail.mail', factory_items)


class TestActionMenu(IntegrationTestCase):

    features = ('optional-task-permissions-revoking', )

    @browsing
    def test_revoke_permissions_is_shown_only_on_tasks_in_final_state(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.subtask)
        self.assertNotIn('Revoke permissions', editbar.menu_options('Actions'))

        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        browser.open(self.subtask)
        self.assertIn('Revoke permissions', editbar.menu_options('Actions'))

    @browsing
    def test_revoke_permissions_is_shown_only_when_feature_is_enabled(self, browser):
        self.login(self.manager, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        browser.open(self.subtask)
        self.assertIn('Revoke permissions', editbar.menu_options('Actions'))

        api.portal.set_registry_record('optional_task_permissions_revoking_enabled',
                                       False, interface=ITaskSettings)
        browser.open(self.subtask)
        self.assertNotIn('Revoke permissions', editbar.menu_options('Actions'))

    @browsing
    def test_revoke_permissions_is_shown_only_for_managers_and_task_issuer(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        # dossier_responsible is task issuer
        browser.open(self.subtask)
        self.assertIn('Revoke permissions', editbar.menu_options('Actions'))

        self.subtask.issuer = self.regular_user.id
        browser.open(self.subtask)
        self.assertNotIn('Revoke permissions', editbar.menu_options('Actions'))

        api.user.grant_roles(user=self.dossier_responsible, roles=['Manager'])
        browser.open(self.subtask)
        self.assertIn('Revoke permissions', editbar.menu_options('Actions'))
