from ftw.builder import Builder
from ftw.builder import create
from opengever.task.interfaces import ISuccessorTaskController
from opengever.testing import FunctionalTestCase
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestSuccessorTaskController(FunctionalTestCase):

    use_default_fixture = False

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
            u'admin-unit-1:%s' % (intids.getId(task1)),
            ISuccessorTaskController(task1).get_oguid())
        self.assertEquals(
            u'admin-unit-1:%s' % (intids.getId(task2)),
            ISuccessorTaskController(task2).get_oguid())

    def test_oguid_by_path_returns_the_oguid_of_the_accordant_task(self):
        intids = getUtility(IIntIds)
        url_tool = getToolByName(self.portal, 'portal_url')

        task = create(Builder('task'))

        controller = ISuccessorTaskController(task)
        self.assertEquals(
            u'admin-unit-1:%s' % (intids.getId(task)),
            controller.get_oguid_by_path(
                '/'.join(url_tool.getRelativeContentPath(task)),
                'admin-unit-1'))

    def test_oguid_by_path_returns_none_for_invalid_admin_unit_id(self):
        task = create(Builder('task'))

        controller = ISuccessorTaskController(task)
        self.assertEquals(
            None,
            controller.get_oguid_by_path('/'.join(task.getPhysicalPath()), 'admin-unit-2'))

    def test_oguid_by_path_returns_none_for_invalid_path(self):
        task = create(Builder('task'))

        controller = ISuccessorTaskController(task)
        self.assertEquals(
            None,
            controller.get_oguid_by_path('/plone/not-existing/', 'admin-unit-1'))

    def test_set_predecessor_with_valid_oguid_returns_true(self):
        task1 = create(Builder('task'))
        task2 = create(Builder('task'))

        task2_oguid = ISuccessorTaskController(task2).get_oguid()
        self.assertTrue(
            ISuccessorTaskController(task1).set_predecessor(task2_oguid))

    def test_set_predecessor_resets_issuing_org_unit_to_predecessors_one(self):
        extra_au = create(Builder('admin_unit').id(u'extra-au'))
        extra_ou = create(Builder('org_unit')
                          .having(admin_unit=extra_au)
                          .id(u'extra-ou'))

        create(Builder('globalindex_task')
               .having(int_id='1234',
                       issuing_org_unit='extra-ou',
                       admin_unit_id='extra-au'))
        successor = create(Builder('task')
                           .having(responsible_client='org-unit-1'))

        self.assertEquals(self.org_unit,
                          successor.get_sql_object().get_issuing_org_unit())

        ISuccessorTaskController(successor).set_predecessor('extra-au:1234')
        self.assertEquals(extra_ou,
                          successor.get_sql_object().get_issuing_org_unit())

    def test_set_predecessor_with_invalid_oguid_returns_false(self):
        task1 = create(Builder('task'))

        self.assertFalse(
            ISuccessorTaskController(task1).set_predecessor(u'incorrect:2'))
        self.assertFalse(
            ISuccessorTaskController(task1).set_predecessor(u'org-unit-1:3'))

    def test_successors_predecessor_relation(self):
        task1 = create(Builder('task'))
        task2 = create(Builder('task'))
        task3 = create(Builder('task'))

        task1_oguid = ISuccessorTaskController(task1).get_oguid()

        task1_sql = task1.get_sql_object()
        task2_sql = task2.get_sql_object()
        task3_sql = task3.get_sql_object()

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
