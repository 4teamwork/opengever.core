from Products.CMFCore.utils import getToolByName
from opengever.task.interfaces import ISuccessorTaskController
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import set_current_client_id
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent


class TestSuccessorTaskController(FunctionalTestCase):

    def test_oguid_of_a_task(self):
        intids = getUtility(IIntIds)
        create_client(clientid='client1')
        set_current_client_id(self.portal)

        task1 = Builder('task').create()
        notify(ObjectCreatedEvent(task1))
        notify(ObjectAddedEvent(task1))

        task2 = Builder('task').create()
        notify(ObjectCreatedEvent(task2))
        notify(ObjectAddedEvent(task2))

        self.assertEquals(
            u'client1:%s' % (intids.getId(task1)),
            ISuccessorTaskController(task1).get_oguid())
        self.assertEquals(
            u'client1:%s' % (intids.getId(task2)),
            ISuccessorTaskController(task2).get_oguid())

    def test_getting_oguid_by_path_for_existing_task(self):
        intids = getUtility(IIntIds)
        url_tool = getToolByName(self.portal, 'portal_url')
        create_client(clientid='client1')
        set_current_client_id(self.portal)

        task = Builder('task').create()
        notify(ObjectCreatedEvent(task))
        notify(ObjectAddedEvent(task))

        sct = ISuccessorTaskController(task)
        self.assertEquals(
            u'client1:%s' % (intids.getId(task)),
            sct.get_oguid_by_path(
                '/'.join(url_tool.getRelativeContentPath(task)),
                'client1'))

    def test_oguid_for_not_existing_path_is_none(self):
        create_client(clientid='client1')
        set_current_client_id(self.portal)

        task = Builder('task').create()
        notify(ObjectCreatedEvent(task))
        notify(ObjectAddedEvent(task))

        sct = ISuccessorTaskController(task)
        self.assertEquals(
            None,
            sct.get_oguid_by_path('/'.join(task.getPhysicalPath()), 'client2'))

    def test_setting_valid_predecessor_returns_true(self):
        create_client(clientid='client1')
        set_current_client_id(self.portal)

        task1 = Builder('task').create()
        notify(ObjectCreatedEvent(task1))
        notify(ObjectAddedEvent(task1))

        task2 = Builder('task').create()
        notify(ObjectCreatedEvent(task2))
        notify(ObjectAddedEvent(task2))

        task2_oguid = ISuccessorTaskController(task2).get_oguid()
        self.assertTrue(
            ISuccessorTaskController(task1).set_predecessor(task2_oguid))

    def test_setting_invalid_predecessor_returns_false(self):
        create_client(clientid='client1')
        set_current_client_id(self.portal)

        task1 = Builder('task').create()
        notify(ObjectCreatedEvent(task1))
        notify(ObjectAddedEvent(task1))

        self.assertFalse(
            ISuccessorTaskController(task1).set_predecessor(u'incorrect:2'))

    def test_successors_predecessor_relation(self):
        create_client(clientid='client1')
        set_current_client_id(self.portal)

        task1 = Builder('task').create()
        notify(ObjectCreatedEvent(task1))
        notify(ObjectAddedEvent(task1))

        task2 = Builder('task').create()
        notify(ObjectCreatedEvent(task2))
        notify(ObjectAddedEvent(task2))

        task3 = Builder('task').create()
        notify(ObjectCreatedEvent(task3))
        notify(ObjectAddedEvent(task3))

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
