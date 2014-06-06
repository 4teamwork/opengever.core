from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from opengever.task.interfaces import ISuccessorTaskController
from opengever.testing import FunctionalTestCase
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestSuccessorTaskController(FunctionalTestCase):

    def setUp(self):
        super(TestSuccessorTaskController, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture')
            .with_user()
            .with_org_unit()
            .with_admin_unit(public_url='http://plone'))

    def test_oguid_is_admin_unit_id_and_task_id_separated_by_a_colon(self):
        intids = getUtility(IIntIds)

        task1 = create(Builder('task'))
        task2 = create(Builder('task'))

        self.assertEquals(
            u'client1:%s' % (intids.getId(task1)),
            ISuccessorTaskController(task1).get_oguid())
        self.assertEquals(
            u'client1:%s' % (intids.getId(task2)),
            ISuccessorTaskController(task2).get_oguid())

    def test_oguid_by_path_returns_the_oguid_of_the_accordant_task(self):
        intids = getUtility(IIntIds)
        url_tool = getToolByName(self.portal, 'portal_url')

        task = create(Builder('task'))

        controller = ISuccessorTaskController(task)
        self.assertEquals(
            u'client1:%s' % (intids.getId(task)),
            controller.get_oguid_by_path(
                '/'.join(url_tool.getRelativeContentPath(task)),
                'client1'))

    def test_oguid_by_path_returns_none_for_invalid_admin_unit_id(self):
        task = create(Builder('task'))

        controller = ISuccessorTaskController(task)
        self.assertEquals(
            None,
            controller.get_oguid_by_path('/'.join(task.getPhysicalPath()), 'client2'))

    def test_oguid_by_path_returns_none_for_invalid_path(self):
        task = create(Builder('task'))

        controller = ISuccessorTaskController(task)
        self.assertEquals(
            None,
            controller.get_oguid_by_path('/plone/not-existing/', 'client1'))

    def test_set_predecessor_with_valid_oguid_returns_true(self):
        task1 = create(Builder('task'))
        task2 = create(Builder('task'))

        task2_oguid = ISuccessorTaskController(task2).get_oguid()
        self.assertTrue(
            ISuccessorTaskController(task1).set_predecessor(task2_oguid))

    def test_set_predecessor_with_invalid_oguid_returns_false(self):
        task1 = create(Builder('task'))

        self.assertFalse(
            ISuccessorTaskController(task1).set_predecessor(u'incorrect:2'))
        self.assertFalse(
            ISuccessorTaskController(task1).set_predecessor(u'client1:3'))

    def test_successors_predecessor_relation(self):
        task1 = create(Builder('task'))
        task2 = create(Builder('task'))
        task3 = create(Builder('task'))

        task1_oguid = ISuccessorTaskController(task1).get_oguid()

        task1_sql = ISuccessorTaskController(task1).get_indexed_data()
        task2_sql = ISuccessorTaskController(task2).get_indexed_data()
        task3_sql = ISuccessorTaskController(task3).get_indexed_data()

        ISuccessorTaskController(task2).set_predecessor(task1_oguid)
        ISuccessorTaskController(task3).set_predecessor(task1_oguid)

        self.assertEquals(
            task1_sql,
            ISuccessorTaskController(task2).get_predecessor())
        self.assertEquals(
            task1_sql,
            ISuccessorTaskController(task3).get_predecessor())

        self.assertEquals(
            [task2_sql, task3_sql],
            ISuccessorTaskController(task1).get_successors())
