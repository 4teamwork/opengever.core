from Products.CMFCore.utils import getToolByName
from ftw.contentmenu.menu import FactoriesMenu
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskPostFactoryMenu(FunctionalTestCase):

    def setUp(self):
        super(TestTaskPostFactoryMenu, self).setUp()
        self.menu = FactoriesMenu(self.portal)
        self.wft = getToolByName(self.portal, 'portal_workflow')

    def test_task_menu_action_in_a_dossier(self):
        dossier = Builder('dossier').create()

        items = self.menu.getMenuItems(dossier, self.portal.REQUEST)
        titles = [item['title'] for item in items]

        self.assertIn(u'Task', titles)
        self.assertNotIn(u'Subtask', titles)

    def test_subtask_menu_action_in_a_task(self):
        task = Builder('task').having(
            title='Task One',
            issuer=TEST_USER_ID,
            responsible=TEST_USER_ID).create()
        self.wft.doActionFor(task, 'task-transition-open-in-progress')

        items = self.menu.getMenuItems(task, self.portal.REQUEST)
        titles = [item['title'] for item in items]

        self.assertNotIn(u'Task', titles)
        self.assertIn(u'Subtask', titles)

    def test_subtask_menu_class_in_a_task(self):
        task = Builder('task').having(
            title='Task One',
            issuer=TEST_USER_ID,
            responsible=TEST_USER_ID).create()
        self.wft.doActionFor(task, 'task-transition-open-in-progress')

        items = self.menu.getMenuItems(task, self.portal.REQUEST)
        task_action = [action for action in items
                       if action.get('id') == 'opengever.task.task'][0]

        self.assertEquals(u'icon-task-subtask',
                          task_action.get('extra').get('class'))

    def test_mail_action_is_not_displayed_in_a_task(self):
        task = Builder('task').having(
            title='Task One',
            issuer=TEST_USER_ID,
            responsible=TEST_USER_ID).create()
        self.wft.doActionFor(task, 'task-transition-open-in-progress')

        items = self.menu.getMenuItems(task, self.portal.REQUEST)
        titles = [item['title'] for item in items]

        self.assertNotIn('mail', titles)
