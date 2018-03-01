from datetime import datetime
from datetime import timedelta
from ftw.testing import MockTestCase
from opengever.base.browser.wizard import storage
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.core.testing import COMPONENT_UNIT_TESTING
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getSiteManager
from zope.component.hooks import setSite
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass
import AccessControl


class TestAcceptTaskStorageManager(MockTestCase):

    layer = COMPONENT_UNIT_TESTING

    def setUp(self):
        super(TestAcceptTaskStorageManager, self).setUp()

        site = self.create_dummy(getSiteManager=getSiteManager)
        alsoProvides(site, IAttributeAnnotatable)
        setSite(site)

    def test_implements_interface(self):
        self.assertTrue(IWizardDataStorage.implementedBy(
                storage.WizardDataStorage))

        verifyClass(IWizardDataStorage,
                    storage.WizardDataStorage)

    def test_get_user_storage(self):
        manager = storage.WizardDataStorage()

        data = manager._get_user_storage()
        self.assertTrue(isinstance(data, PersistentDict))

        data['foo'] = 'bar'
        self.assertEqual(manager._get_user_storage(), data)

    def test_drop_data(self):
        manager = storage.WizardDataStorage()
        manager.get_data('somekey')
        self.assertTrue('somekey' in manager._get_user_storage())

        manager.drop_data('somekey')
        self.assertFalse('somekey' in manager._get_user_storage())

    def test_get_user_storage_is_per_user(self):
        request = object()

        john = AccessControl.users.SimpleUser('john', 'pwd', [], [])
        jane = AccessControl.users.SimpleUser('john', 'pwd', [], [])
        login = AccessControl.SecurityManagement.newSecurityManager

        manager = storage.WizardDataStorage()

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

    def test_protected_get_data_initializes_empty_dict(self):
        manager = storage.WizardDataStorage()
        manager.get_data('data-set-key')
        self.assertEqual({}, manager.get_data('data-set-key'))

        self.assertEqual(set(manager._get_user_storage().keys()),
                         set(['data-set-key']))

    def test_protected_get_data_contains_created_timestamp(self):
        manager = storage.WizardDataStorage()
        data = manager._get_data('something')
        self.assertEqual(['__created'], data.keys())
        self.assertIsNotNone(data['__created'])
        self.assertIsInstance(data['__created'], datetime)

    def test_public_get_data_returns_copy(self):
        manager = storage.WizardDataStorage()
        manager.get_data('something')

        self.assertIsNot(manager.get_data('something'),
                         manager._get_data('something'))

    def test_data_expires(self):
        manager = storage.WizardDataStorage()
        veryold = datetime.now() - timedelta(days=100)

        manager.get_data('one')
        manager.get_data('two')
        self.assertEqual(set(manager._get_user_storage().keys()),
                         set(['one', 'two']))

        manager._get_data('one')['__created'] = veryold

        manager.get_data('two')
        self.assertEqual(manager._get_user_storage().keys(), ['two'])

    def test_update(self):
        manager = storage.WizardDataStorage()

        manager.set('one', 'foo', 'qux')
        self.assertEqual({'foo': 'qux'}, manager.get_data('one'))

        manager.update('one', {'foo': 'bar',
                               'foobar': 'baz'})
        self.assertEqual({'foo': 'bar',
                          'foobar': 'baz'}, manager.get_data('one'), )
        self.assertEqual(manager.get_data('one')['foo'], 'bar')

    def test_set_and_get(self):
        manager = storage.WizardDataStorage()

        manager.set('data-set-key', 'mykey', 'myvalue')
        self.assertEqual(manager.get('data-set-key', 'mykey'), 'myvalue')
        self.assertEqual(manager.get('data-set-key', 'non-existing'), None)

        self.assertEqual(
            manager.get('data-set-key', 'non-existing', 'another-default'),
            'another-default')
