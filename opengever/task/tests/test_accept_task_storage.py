from datetime import datetime
from datetime import timedelta
from ftw.testing import MockTestCase
from opengever.task.browser.accept import storage
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.testing import ANNOTATION_LAYER
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.hooks import setSite
from zope.interface import Interface
from zope.interface.verify import verifyClass
import AccessControl


class TestAcceptTaskStorageManager(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        site = self.providing_stub([IAttributeAnnotatable])
        setSite(site)

        self.task_controller = self.stub()
        self.mock_adapter(self.task_controller, ISuccessorTaskController,
                          (Interface,))

    def test_implements_interface(self):
        self.replay()
        self.assertTrue(storage.IAcceptTaskStorageManager.implementedBy(
                storage.AcceptTaskStorageManager))

        verifyClass(storage.IAcceptTaskStorageManager,
                    storage.AcceptTaskStorageManager)

    def test_get_user_storage(self):
        self.replay()
        manager = storage.AcceptTaskStorageManager()

        data = manager._get_user_storage()
        self.assertTrue(isinstance(data, PersistentDict))

        data['foo'] = 'bar'
        self.assertEqual(manager._get_user_storage(), data)

    def test_get_user_storage_is_per_user(self):
        request = object()
        self.replay()

        john = AccessControl.users.SimpleUser('john', 'pwd', [], [])
        jane = AccessControl.users.SimpleUser('john', 'pwd', [], [])
        login = AccessControl.SecurityManagement.newSecurityManager

        manager = storage.AcceptTaskStorageManager()

        try:
            login(request, john)
            john_data = manager._get_user_storage()
            john_data['john'] = 'john.doe'

            login(request, jane)
            jane_data = manager._get_user_storage()
            jane_data['jane'] = 'jane.doe'

            login(request, john)
            self.assertEqual(manager._get_user_storage(), john_data)

            login(request, jane)
            self.assertEqual(manager._get_user_storage(), jane_data)

        except:
            AccessControl.SecurityManagement.noSecurityManager()

        else:
            AccessControl.SecurityManagement.noSecurityManager()

    def test_get_data_requires_argument(self):
        self.replay()
        manager = storage.AcceptTaskStorageManager()

        with self.assertRaises(TypeError) as cm:
            manager.get_data()

        self.assertEqual(str(cm.exception),
                         'Either oguid or task required.')

    def test_get_data_only_accepts_oguid_or_task(self):
        self.replay()
        manager = storage.AcceptTaskStorageManager()

        with self.assertRaises(TypeError) as cm:
            manager.get_data('a:b', object())

        self.assertEqual(str(cm.exception),
                         'Only one of oguid and task can be used.')

    def test_get_data(self):
        task = self.mocker.mock()
        task_oguid = 'client1:mytask'

        self.expect(self.task_controller(task).get_oguid()).result(task_oguid)
        self.replay()

        manager = storage.AcceptTaskStorageManager()
        task_data = manager.get_data(task=task)
        task_data['foo'] = 'bar'
        self.assertEqual(manager.get_data(task_oguid), task_data)

        task2_oguid = 'client2:othertask'
        task2_data = manager.get_data(task2_oguid)
        task2_data['task2'] = 'bar'
        self.assertEqual(manager.get_data(task2_oguid), task2_data)

        self.assertNotEqual(manager.get_data(task_oguid),
                            manager.get_data(task2_oguid))

        self.assertEqual(manager._get_user_storage().keys(),
                         [task_oguid, task2_oguid])

    def test_data_expires(self):
        self.replay()
        manager = storage.AcceptTaskStorageManager()
        veryold = datetime.now() - timedelta(days=100)

        manager.get_data('one')
        manager.get_data('two')
        self.assertEqual(set(manager._get_user_storage().keys()),
                         set(['one', 'two']))

        manager.get_data('one')['__created'] = veryold
        manager.get_data('two')
        self.assertEqual(manager._get_user_storage().keys(), ['two'])

    def test_update(self):
        self.replay()
        manager = storage.AcceptTaskStorageManager()

        manager.get_data('one')
        self.assertEqual(set(manager.get_data('one').keys()),
                         set(['__created']))

        manager.update({'foo': 'bar',
                        'foobar': 'baz'},
                       oguid='one')
        self.assertEqual(set(manager.get_data('one').keys()),
                         set(['__created', 'foo', 'foobar']))

        self.assertEqual(manager.get_data('one')['foo'], 'bar')

    def test_set_and_get(self):
        self.replay()
        manager = storage.AcceptTaskStorageManager()

        manager.set('mykey', 'myvalue', oguid='myoguid')
        self.assertEqual(manager.get('mykey', oguid='myoguid'), 'myvalue')
