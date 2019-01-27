from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.webactions.interfaces import IWebActionsStorage
from opengever.webactions.storage import get_storage
from opengever.webactions.storage import WebActionsStorage
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestWebActionsStorageInitialization(IntegrationTestCase):

    def test_implements_interface(self):
        storage = get_storage()
        verifyObject(IWebActionsStorage, storage)
        verifyClass(IWebActionsStorage, WebActionsStorage)

    def test_storage_gets_initialized(self):
        ann = IAnnotations(self.portal)
        storage = get_storage()

        self.assertTrue(storage._storage is ann[WebActionsStorage.ANNOTATIONS_KEY])
        self.assertIsInstance(storage._storage, OOBTree)

        self.assertTrue(storage._actions is storage._storage[WebActionsStorage.STORAGE_ACTIONS_KEY])
        self.assertIsInstance(storage._actions, IOBTree)

        self.assertEquals(0, storage._storage['next_id'])

    def test_initialization_is_idempotent(self):
        storage = get_storage()
        action = create(Builder('webaction'))

        # Multiple initializations shouldn't remove existing data
        storage.initialize_storage()

        action_from_storage = storage.get(0)
        self.assertEqual(action, action_from_storage)
        self.assertEqual(1, storage._storage['next_id'])


class TestWebActionsStorageIDGeneration(IntegrationTestCase):

    def test_new_action_id_for_empty_storage_is_zero(self):
        storage = get_storage()

        new_action_id = storage.issue_new_action_id()
        self.assertEqual(0, new_action_id)

    def test_new_action_id_is_based_on_a_counter_in_storage(self):
        storage = get_storage()

        storage._storage['next_id'] = 42
        self.assertEqual(42, storage.issue_new_action_id())
        self.assertEqual(43, storage._storage['next_id'])

        new_action = create(Builder('webaction'))
        self.assertEqual(43, new_action['action_id'])


class TestWebActionsStorageAdding(IntegrationTestCase):

    def test_add_webaction(self):
        self.login(self.manager)

        storage = get_storage()
        new_action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'enabled': True,
            'icon_name': 'fa-helicopter',
            'display': 'title-buttons',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'types': ['opengever.dossier.businesscasedossier'],
            'groups': ['some-group'],
            'permissions': ['add:opengever.document.document'],
            'comment': u'Lorem Ipsum',
            'unique_name': u'open-in-external-app-title-action',
        }

        with freeze(datetime(2019, 12, 31, 17, 45)):
            action_id = storage.add(new_action)

        self.assertEqual(1, len(storage.list()))
        action_from_storage = storage.get(action_id)

        expected = new_action.copy()
        expected.update({
            'action_id': 0,
            'created': datetime(2019, 12, 31, 17, 45),
            'modified': datetime(2019, 12, 31, 17, 45),
            'owner': 'admin',
        })

        self.assertEqual(expected, action_from_storage)
        self.assertIsInstance(action_from_storage, PersistentMapping)


class TestWebActionsStorageRetrieval(IntegrationTestCase):

    def test_get_webaction(self):
        storage = get_storage()
        action = create(Builder('webaction'))
        self.assertEqual(action, storage.get(0))

    def test_get_webaction_for_missing_action_raises_key_error(self):
        storage = get_storage()
        with self.assertRaises(KeyError):
            storage.get(42)

    def test_list_webactions(self):
        storage = get_storage()
        action1 = create(Builder('webaction').titled(u'Action 1'))
        action2 = create(Builder('webaction').titled(u'Action 2'))
        self.assertEqual([action1, action2], [dict(a) for a in storage.list()])

    def test_list_webactions_on_empty_storage_returns_empty_list(self):
        storage = get_storage()
        self.assertEqual([], storage.list())


class TestWebActionsStorageUpdating(IntegrationTestCase):

    def test_update_webaction(self):
        self.login(self.manager)

        storage = get_storage()
        with freeze(datetime(2019, 12, 31, 17, 45)):
            action = create(Builder('webaction').titled(u'Open in ExternalApp')
                            .having(
                                title=u'Open in ExternalApp',
                                target_url='http://example.org/endpoint',
            ))
        action_id = action['action_id']
        self.assertEqual(action, storage.get(action_id))

        with freeze(datetime(2020, 7, 31, 19, 15)):
            storage.update(action_id, {'title': u'My new title'})

        self.assertIsInstance(storage.get(action_id), PersistentMapping)
        self.assertEqual({
            'action_id': 0,
            'title': u'My new title',
            'target_url': 'http://example.org/endpoint',
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'created': datetime(2019, 12, 31, 17, 45),
            'modified': datetime(2020, 7, 31, 19, 15),
            'owner': 'admin',
        }, storage.get(action_id))

    def test_updating_non_existing_webaction_raises_key_error(self):
        storage = get_storage()

        with self.assertRaises(KeyError):
            storage.update(77, {'title': u'This action does not exist'})


class TestWebActionsStorageDeletion(IntegrationTestCase):

    def test_delete_webaction(self):
        storage = get_storage()
        action = create(Builder('webaction'))
        storage.delete(action['action_id'])
        self.assertEqual(0, len(storage._actions))
        self.assertEqual({}, dict(storage._actions))

    def test_delete_for_non_existent_webaction_raises_key_error(self):
        storage = get_storage()
        with self.assertRaises(KeyError):
            storage.delete(77)
