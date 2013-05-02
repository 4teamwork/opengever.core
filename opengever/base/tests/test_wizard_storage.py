from datetime import datetime
from datetime import timedelta
from ftw.testing import MockTestCase
from opengever.base.browser.wizard import storage
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.core.testing import ANNOTATION_LAYER
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.hooks import setSite
from zope.component import getSiteManager
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass
import AccessControl


class TestAcceptTaskStorageManager(MockTestCase):

    layer = ANNOTATION_LAYER

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

    def test_get_data(self):

        manager = storage.WizardDataStorage()
        data = manager.get_data('data-set-key')
        data['foo'] = 'bar'
        self.assertEqual(manager.get_data('data-set-key'), data)

        data2 = manager.get_data('other-data-set-key')
        data2['task2'] = 'bar'
        self.assertEqual(manager.get_data('other-data-set-key'), data2)

        self.assertNotEqual(manager.get_data('data-set-key'),
                            manager.get_data('other-data-set-key'))

        self.assertEqual(set(manager._get_user_storage().keys()),
                         set(['data-set-key', 'other-data-set-key']))

    def test_data_expires(self):
        manager = storage.WizardDataStorage()
        veryold = datetime.now() - timedelta(days=100)

        manager.get_data('one')
        manager.get_data('two')
        self.assertEqual(set(manager._get_user_storage().keys()),
                         set(['one', 'two']))

        manager.get_data('one')['__created'] = veryold
        manager.get_data('two')
        self.assertEqual(manager._get_user_storage().keys(), ['two'])

    def test_update(self):
        manager = storage.WizardDataStorage()

        manager.get_data('one')
        self.assertEqual(set(manager.get_data('one').keys()),
                         set(['__created']))

        manager.update('one', {'foo': 'bar',
                               'foobar': 'baz'})
        self.assertEqual(set(manager.get_data('one').keys()),
                         set(['__created', 'foo', 'foobar']))

        self.assertEqual(manager.get_data('one')['foo'], 'bar')

    def test_set_and_get(self):
        manager = storage.WizardDataStorage()

        manager.set('data-set-key', 'mykey', 'myvalue')
        self.assertEqual(manager.get('data-set-key', 'mykey'), 'myvalue')
        self.assertEqual(manager.get('data-set-key', 'non-existing'), None)

        self.assertEqual(
            manager.get('data-set-key', 'non-existing', 'another-default'),
            'another-default')
