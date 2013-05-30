from ftw.contentmenu.menu import FactoriesMenu
from opengever.testing import Builder
from opengever.testing import create
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter


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

        self.assert_removed_menu_item('ftw.mail.mail', context=task)

    def assert_removed_menu_item(self, removed_item, context):
        factories_view = getMultiAdapter(
            (context, self.portal.REQUEST), name='folder_factories')
        factories_view.addable_types(include=None)
        all_items = [item.get('id') for item
                     in factories_view.addable_types(include=None)]

        items = self.menu.getMenuItems(context, self.portal.REQUEST)
        filtered_items = [item.get('id') for item in items]

        self.assertEquals(set([removed_item,]),
                          set(all_items)-set(filtered_items))
