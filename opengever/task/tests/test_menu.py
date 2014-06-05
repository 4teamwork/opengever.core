from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestFactoryMenu(FunctionalTestCase):

    def setUp(self):
        super(TestFactoryMenu, self).setUp()
        self.menu = FactoriesMenu(self.portal)

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

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
