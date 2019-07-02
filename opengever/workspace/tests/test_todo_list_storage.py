from opengever.testing import IntegrationTestCase
from opengever.workspace.todos.storage import ToDoListStorage
from opengever.workspace.todos.storage import ToDoListStorageError
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from zope.schema.interfaces import ValidationError


class TestToDoListStorage(IntegrationTestCase):

    def test_storage_gets_initialized(self):
        self.login(self.workspace_member)
        ann = IAnnotations(self.workspace)
        storage = ToDoListStorage(self.workspace)

        self.assertTrue(storage._storage is ann[ToDoListStorage.ANNOTATIONS_KEY])
        self.assertTrue(storage._todo_lists is storage._storage[ToDoListStorage.TODO_LISTS_KEY])
        self.assertIsInstance(storage._storage, PersistentMapping)
        self.assertIsInstance(storage._todo_lists, PersistentList)

        self.assertEqual(0, len(storage._todo_lists))

    def test_initialization_is_idempotent(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        storage.create_todo_list(u'01 - General')

        # Multiple initializations shouldn't remove existing data
        self.assertEqual(1, len(storage._todo_lists))
        storage._initialize_storage()
        self.assertEqual(1, len(storage._todo_lists))

    def test_todo_list_title_is_required(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        with self.assertRaises(ValidationError):
            storage.create_todo_list(u'')

    def test_list_returns_stored_todo_lists(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)

        list_1 = storage.create_todo_list(u'01 - General')
        list_2 = storage.create_todo_list(u'02 - Server')

        self.assertEqual([list_2, list_1], storage.list())

    def test_list_serialized_returns_stored_serialized_todo_lists(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)

        list_1 = storage.create_todo_list(u'01 - General')
        storage.add_todo_to_list(list_1.id, 'todo-1')

        list_2 = storage.create_todo_list(u'02 - Server')

        self.assertEqual(
            [
                {
                    '@id': list_2.id,
                    '@type': 'virtual.workspace.todolist',
                    'UID': list_2.id,
                    'title': u'02 - Server',
                    'todos': []
                },
                {
                    '@id': list_1.id,
                    '@type': 'virtual.workspace.todolist',
                    'UID': list_1.id,
                    'title': u'01 - General',
                    'todos': ['todo-1']
                }
            ], storage.list_serialized())

    def test_list_serialized_allows_context_based_id_generation(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)

        list_1 = storage.create_todo_list(u'01 - General')

        self.assertEqual(
            [
                {
                    '@id': '{}/@todolist/{}'.format(self.workspace.absolute_url(), list_1.id),
                    '@type': 'virtual.workspace.todolist',
                    'UID': list_1.id,
                    'title': u'01 - General',
                    'todos': []
                }
            ], storage.list_serialized(self.workspace))

    def test_create_todo_list_generate_uuid_for_list(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        todo_list_1 = storage.create_todo_list(u'01 - General')
        todo_list_2 = storage.create_todo_list(u'01 - General')

        self.assertNotEqual(todo_list_1.id,
                            todo_list_2.id)

    def test_create_todo_list_adds_the_list_on_the_first_position_by_default(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        list_1 = storage.create_todo_list(u'01 - General')
        list_2 = storage.create_todo_list(u'02 - Server')

        self.assertEqual([list_2, list_1], storage.list())

    def test_rename_todo_list_renames_the_todo_list(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        storage.create_todo_list(u'01 - General')
        storage.create_todo_list(u'02 - Server')
        todo_list_id = storage.create_todo_list(u'01 - Development').id

        self.assertEqual(
            ['01 - Development', '02 - Server', '01 - General'],
            [todo_list.title for todo_list in storage.list()])

        storage.rename_todo_list(todo_list_id, '03 - Development')

        self.assertEqual(
            ['03 - Development', '02 - Server', '01 - General'],
            [todo_list.title for todo_list in storage.list()])

    def test_rename_todo_list_raises_an_exception_if_title_is_empty(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        todo_list_id = storage.create_todo_list(u'01 - General').id

        with self.assertRaises(ValidationError):
            storage.rename_todo_list(todo_list_id, '')

    def test_remove_todo_list_by_id_removes_list(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        todo_list_1 = storage.create_todo_list(u'01 - General')
        todo_list_2 = storage.create_todo_list(u'02 - Server')

        self.assertItemsEqual([todo_list_1, todo_list_2], storage.list())

        storage.remove_todo_list_by_id(todo_list_2.id)

        self.assertItemsEqual([todo_list_1], storage.list())

    def test_disallow_removing_todo_list_if_todos_are_assigned_to_it(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        todo_list_id = storage.create_todo_list(u'01 - General').id
        storage.add_todo_to_list(todo_list_id, 'uid-2')

        with self.assertRaises(ToDoListStorageError):
            storage.remove_todo_list_by_id(todo_list_id)

    def test_add_todo_to_list_to_not_existing_list_raises_an_error(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)

        with self.assertRaises(ToDoListStorageError):
            storage.add_todo_to_list('missing-list-id', '123')

    def test_add_todo_to_list(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)

        list_id_1 = storage.create_todo_list(u'01 - General').id
        list_id_2 = storage.create_todo_list(u'02 - Server').id
        storage.add_todo_to_list(list_id_2, 'uid-2')
        storage.add_todo_to_list(list_id_2, 'uid-5')

        self.assertEqual([], storage._get_todo_list_by_id(list_id_1).todos)
        self.assertEqual(['uid-2', 'uid-5'],
                         storage._get_todo_list_by_id(list_id_2).todos)

    def test_remove_not_existing_todo_raises_an_error(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        storage.create_todo_list(u'01 - General').id

        with self.assertRaises(ToDoListStorageError):
            storage.remove_todo_from_current_list('missing-uid')

    def test_remove_todo_from_current_list(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)

        list_id_1 = storage.create_todo_list(u'01 - General').id
        storage.add_todo_to_list(list_id_1, 'uid-3')

        list_id_2 = storage.create_todo_list(u'02 - Server').id
        storage.add_todo_to_list(list_id_2, 'uid-2')

        storage.remove_todo_from_current_list('uid-2')

        self.assertEqual(['uid-3'], storage._get_todo_list_by_id(list_id_1).todos)
        self.assertEqual([],
                         storage._get_todo_list_by_id(list_id_2).todos)

    def test_move_todo_list_to_new_position(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        list_id = storage.create_todo_list(u'First').id
        storage.create_todo_list(u'Second').id
        storage.create_todo_list(u'Third').id

        self.assertEqual(['Third', 'Second', 'First'],
                         [tl.title for tl in storage._todo_lists])

        storage.move_todo_list(list_id, 0)

        self.assertEqual(['First', 'Third', 'Second'],
                         [tl.title for tl in storage._todo_lists])

        storage.move_todo_list(list_id, 50)

        self.assertEqual(['Third', 'Second', 'First'],
                         [tl.title for tl in storage._todo_lists])

        storage.move_todo_list(list_id, 1)

        self.assertEqual(['Third', 'First', 'Second'],
                         [tl.title for tl in storage._todo_lists])

        storage.move_todo_list(list_id, -2)

        self.assertEqual(['First', 'Third', 'Second'],
                         [tl.title for tl in storage._todo_lists])

    def test_move_not_existing_todo_list_raises_an_error(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)

        with self.assertRaises(ToDoListStorageError):
            storage.move_todo_list('invalid-list-id', 0)

    def test_move_todo_in_same_list(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        list_id = storage.create_todo_list(u'01 - General').id
        storage.add_todo_to_list(list_id, 'uid-1')
        storage.add_todo_to_list(list_id, 'uid-2')
        storage.add_todo_to_list(list_id, 'uid-3')

        self.assertEqual(
            ['uid-1', 'uid-2', 'uid-3'],
            storage._get_todo_list_by_id(list_id).todos)

        storage.move_todo(list_id, 'uid-3', 0)
        self.assertEqual(
            ['uid-3', 'uid-1', 'uid-2'],
            storage._get_todo_list_by_id(list_id).todos)

    def test_move_todo_to_a_different_list(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        list_id_1 = storage.create_todo_list(u'01 - General').id
        storage.add_todo_to_list(list_id_1, 'uid-1')
        storage.add_todo_to_list(list_id_1, 'uid-2')
        storage.add_todo_to_list(list_id_1, 'uid-3')

        list_id_2 = storage.create_todo_list(u'02 - Server').id
        storage.add_todo_to_list(list_id_2, 'uid-4')
        storage.add_todo_to_list(list_id_2, 'uid-5')
        storage.add_todo_to_list(list_id_2, 'uid-6')

        self.assertEqual(
            ['uid-1', 'uid-2', 'uid-3'],
            storage._get_todo_list_by_id(list_id_1).todos)

        self.assertEqual(
            ['uid-4', 'uid-5', 'uid-6'],
            storage._get_todo_list_by_id(list_id_2).todos)

        storage.move_todo(list_id_2, 'uid-3', 1)

        self.assertEqual(
            ['uid-1', 'uid-2'],
            storage._get_todo_list_by_id(list_id_1).todos)

        self.assertEqual(
            ['uid-4', 'uid-3', 'uid-5', 'uid-6'],
            storage._get_todo_list_by_id(list_id_2).todos)

    def test_move_not_existing_todo_raises_an_error(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        list_id = storage.create_todo_list(u'01 - General').id
        storage.add_todo_to_list(list_id, 'uid-1')

        with self.assertRaises(ToDoListStorageError):
            storage.move_todo(list_id, 'not-existing-todo-uid', 0)

    def test_move_todo_to_a_not_exisiting_todo_list_raises_an_error(self):
        self.login(self.workspace_member)
        storage = ToDoListStorage(self.workspace)
        list_id = storage.create_todo_list(u'01 - General').id
        storage.add_todo_to_list(list_id, 'uid-1')

        with self.assertRaises(ToDoListStorageError):
            storage.move_todo('invalid-list-id', 'uid-1', 0)
