from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.webactions.interfaces import IWebActionsStorage
from opengever.webactions.storage import ActionAlreadyExists
from opengever.webactions.storage import get_storage
from opengever.webactions.storage import WebActionsStorage
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
from zope.schema import ValidationError


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

        self.assertTrue(storage._indexes is storage._storage[WebActionsStorage.STORAGE_INDEXES_KEY])
        self.assertIsInstance(storage._indexes, OOBTree)

        self.assertIsInstance(storage._indexes[WebActionsStorage.IDX_UNIQUE_NAME], OIBTree)

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

    BASE64_ENCODED_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='  # noqa

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

    def test_add_webaction_with_missing_fields_raises(self):
        storage = get_storage()
        action = {}

        with self.assertRaises(ValidationError) as cm:
            storage.add(action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "('title', RequiredMissing('title'))).",
            cm.exception.message)

    def test_icon_required_for_certain_display_locations(self):
        storage = get_storage()
        new_action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'display': 'title-buttons',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
        }

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "(None, Invalid(\"Display location 'title-buttons' requires an icon.\",))).",
            cm.exception.message)

    def test_icon_not_allowed_for_certain_display_locations(self):
        storage = get_storage()
        new_action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'icon_name': 'fa-helicopter',
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
        }

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "(None, Invalid(\"Display location 'actions-menu' doesn't allow an icon.\",))).",
            cm.exception.message)

    def test_at_most_one_icon_allowed(self):
        storage = get_storage()
        new_action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'icon_name': 'fa-helicopter',
            'icon_data': 'data:image/png;base64,%s' % self.BASE64_ENCODED_PNG,
            'display': 'title-buttons',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
        }

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "(None, Invalid(\"Icon properties ['icon_name', 'icon_data'] are "
            "mutually exclusive. At most one icon allowed.\",))).",
            cm.exception.message)

    def test_rejects_invalid_data_uris_for_icon_data(self):
        storage = get_storage()
        new_action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'display': 'title-buttons',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
        }

        # Not an URI at all
        new_action['icon_data'] = 'foo'

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "('icon_data', InvalidURI('foo'))).",
            cm.exception.message)

        # Not a data URI
        new_action['icon_data'] = 'http://foo'

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "('icon_data', InvalidBase64DataURI('http://foo'))).",
            cm.exception.message)

        # No base64 encoding declared
        new_action['icon_data'] = 'data:image/png,%s' % self.BASE64_ENCODED_PNG

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "('icon_data', InvalidBase64DataURI('Data URI does not seem to declare base64 encoding.'))).",
            cm.exception.message)

        # Missing mimetype
        new_action['icon_data'] = 'data:base64,%s' % self.BASE64_ENCODED_PNG

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "('icon_data', InvalidBase64DataURI('Data URI does not seem to declare a mimetype.'))).",
            cm.exception.message)

        # Not actually base64 encoded
        new_action['icon_data'] = 'data:image/png;base64,foo'  # noqa

        with self.assertRaises(ValidationError) as cm:
            storage.add(new_action)

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "('icon_data', InvalidBase64DataURI(\"Data URI could not be decoded as base64 (Error('Incorrect padding',)).\"))).",  # noqa
            cm.exception.message)

    def test_cant_add_webaction_with_same_unique_name_twice(self):
        storage = get_storage()
        new_action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'unique_name': u'open-in-external-app-title-action',
        }

        with freeze(datetime(2019, 12, 31, 17, 45)):
            action_id = storage.add(new_action)

        self.assertEqual(1, len(storage.list()))
        action_from_storage = storage.get(action_id)
        self.assertEqual(u'Open in ExternalApp', action_from_storage['title'])

        # Same unique_name, just a different title. Should be rejected.
        new_action['title'] = u'Launch in ExternalApp'
        with self.assertRaises(ActionAlreadyExists) as cm:
            storage.add(new_action)

        self.assertEqual(
            "An action with the unique_name u'open-in-external-app-title-action' already exists",
            cm.exception.message)

    def test_adding_action_correctly_updates_unique_name_index(self):
        storage = get_storage()
        new_action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'unique_name': u'open-in-external-app-title-action',
        }
        action_id = storage.add(new_action)

        unique_name_index = storage._indexes[WebActionsStorage.IDX_UNIQUE_NAME]
        self.assertIn(
            u'open-in-external-app-title-action',
            unique_name_index)

        self.assertEquals(
            action_id,
            unique_name_index[u'open-in-external-app-title-action'])


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

    def test_updating_unique_name_enforces_uniqueness(self):
        storage = get_storage()

        existing_action = create(Builder('webaction')
                                 .having(unique_name=u'existing-unique-name'))

        action_to_update = create(Builder('webaction'))

        with self.assertRaises(ActionAlreadyExists) as cm:
            storage.update(
                action_to_update['action_id'],
                {'unique_name': existing_action['unique_name']})

        self.assertEqual(
            "An action with the unique_name u'existing-unique-name' already exists",
            cm.exception.message)

    def test_update_webaction_with_invalid_fields_raises(self):
        storage = get_storage()
        action = create(Builder('webaction')
                        .having(
                            title=u'Open in ExternalApp',
                            target_url='http://example.org/endpoint',
        ))
        action_id = action['action_id']
        self.assertEqual(action, storage.get(action_id))

        with self.assertRaises(ValidationError) as cm:
            storage.update(action_id, {'target_url': 'not-an-url'})

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "('target_url', InvalidURI('not-an-url'))).",
            cm.exception.message)

    def test_invariants_are_validated_on_final_resulting_object(self):
        """When updating, we need to make sure that invariants are validated
        on the final object that would result from the change (an invariant
        might impose a constraint that involves a field that already exists
        on the object and isn't touched by the update, and one that is being
        changed by the update).
        """
        self.login(self.manager)

        storage = get_storage()
        # We start with an action in the 'title-buttons' display location,
        # which requires an icon, and an value for icon_name property.
        # This is valid so far, no invariants are violated.
        with freeze(datetime(2019, 12, 31, 17, 45)):
            action = create(Builder('webaction').titled(u'Open in ExternalApp')
                            .having(
                                icon_name='fa-helicopter',
                                display='title-buttons',
            ))
        action_id = action['action_id']

        # But if we now attempt to change the display location to the
        # 'actions-menu', which doesn't allow for an icon, the invariant will
        # be violated.
        with self.assertRaises(ValidationError) as cm:
            storage.update(action_id, {'display': 'actions-menu'})

        self.assertEqual(
            "WebAction doesn't conform to schema (First error: "
            "(None, Invalid(\"Display location 'actions-menu' doesn't allow an icon.\",))).",
            cm.exception.message)

        # If we however change both the properties covered by the invariant in
        # the same update, the change succeeds:
        with freeze(datetime(2020, 7, 31, 19, 15)):
            storage.update(action_id, {'display': 'actions-menu', 'icon_name': None})

        self.assertEqual({
            'action_id': 0,
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'icon_name': None,
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'created': datetime(2019, 12, 31, 17, 45),
            'modified': datetime(2020, 7, 31, 19, 15),
            'owner': 'admin',
        }, storage.get(action_id))

    def test_updating_unique_name_correctly_updates_index(self):
        storage = get_storage()

        action = create(Builder('webaction')
                        .having(unique_name=u'open-in-external-app-title-action'))

        unique_name_index = storage._indexes[WebActionsStorage.IDX_UNIQUE_NAME]
        # Guard assertion to verify first version of action is indexed
        self.assertEquals(
            action['action_id'],
            unique_name_index[u'open-in-external-app-title-action'])

        storage.update(action['action_id'], {'unique_name': u'new-unique-id'})

        # Old index entry should have been removed
        self.assertNotIn(
            u'open-in-external-app-title-action',
            unique_name_index)

        # New index entry should have been added
        self.assertEquals(
            action['action_id'],
            unique_name_index[u'new-unique-id'])


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

    def test_deleting_action_correctly_updates_unique_name_index(self):
        storage = get_storage()

        action = create(Builder('webaction')
                        .having(unique_name=u'open-in-external-app-title-action'))

        unique_name_index = storage._indexes[WebActionsStorage.IDX_UNIQUE_NAME]
        # Guard assertion to verify first version of action is indexed
        self.assertEquals(
            action['action_id'],
            unique_name_index[u'open-in-external-app-title-action'])

        storage.delete(action['action_id'])

        # Index entry should have been removed
        self.assertNotIn(
            u'open-in-external-app-title-action',
            unique_name_index)
