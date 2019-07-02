from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from zope.schema.interfaces import ValidationError
import uuid


class ToDoList(Persistent):
    """Lightweight object representing a ToDoList.
    """

    @classmethod
    def create(cls, title):
        if not title:
            raise ValidationError

        return cls(cls.generate_uid(), title)

    @classmethod
    def generate_uid(cls):
        return uuid.uuid4().hex

    def __init__(self, list_id, title):
        self.id = list_id
        self.title = title
        self.todos = PersistentList()

    def serialize(self, context=None):
        _id = '{}/@todolist/{}'.format(context.absolute_url(), self.id) \
              if context else self.id

        return {
            '@id': _id,
            '@type': 'virtual.workspace.todolist',
            'title': self.title,
            'UID': self.id,
            'todos': list(self.todos)
        }

    def rename(self, title):
        if not title:
            raise ValidationError
        self.title = title
        return self

    def add_todo(self, todo_uid):
        if todo_uid not in self.todos:
            self.todos.append(todo_uid)
        return self

    def remove_todo(self, todo_uid):
        self.todos.remove(todo_uid)
        return self


class ToDoListStorageError(Exception):
    """
    """


class ToDoListStorage(object):
    """Stores todo-lists with its related todos in annotations on a workspace.

    Todo-lists are used to manage todos in lists. This feature is only available
    with the new gever-frontend.
    """

    ANNOTATIONS_KEY = 'opengever.workspace.todos.todoliststorage'
    TODO_LISTS_KEY = 'todolists'

    def __init__(self, context):
        self.context = context
        self._storage = None
        self._initialize_storage()

    def create_todo_list(self, title):
        """Creates a todo_list and adds it to the todo-list stack.

        A new todo-list with the given title will be created and added to
        the stack of todo-lists. Per Default, the todo-list will be added at
        the first position due to usability reasons.

        While creating a new todo-list, a new ID for this list will be generated
        and set to this todo-list.

        arguments:
        title -- the title of the new todo-list
        """
        todo_list = ToDoList.create(title)
        self._insert_todo_list_in_storage(todo_list)
        return todo_list

    def remove_todo_list_by_id(self, list_id):
        """Removes a todo_list.

        It is not possible to remove a todo-list havin assigned todos.

        arguments:
        list_id -- The ID of the todo-list you want to remove
        """
        todo_list = self._get_todo_list_by_id(list_id)

        if len(todo_list.todos) > 0:
            raise ToDoListStorageError(
                "Removing a list with assigned todos is not allowed.")

        return self._pop_todo_list(list_id)

    def rename_todo_list(self, list_id, title):
        """Renames a todo-list

        arguments:
        list_id -- The ID of the todo-list you want to remove
        title -- the new title of the todo-list
        """
        return self._get_todo_list_by_id(list_id).rename(title)

    def add_todo_to_list(self, list_id, todo_uid):
        """Adds a todo to a toto-list.

        Adds the given todo_uid to the given todo-list.

        arguments:
        list_id -- The ID of the todo-list you want to remove
        todo_uid -- Existing UID of a todo-object
        """
        return self._get_todo_list_by_id(list_id).add_todo(todo_uid)

    def remove_todo_from_current_list(self, todo_uid):
        """Removes a todo from it currently assigned todo-list.

        arguments:
        todo_uid -- UID of a todo-object
        """
        return self._get_todo_list_by_todo_uid(todo_uid).remove_todo(todo_uid)

    def move_todo(self, list_id, todo_uid, position):
        """Moves a todo to a new position in the given list.

        arguments:
        list_id -- The ID of the todo-list
        todo_uid -- UID of a todo-object
        position -- New position in the given list
        """
        self.remove_todo_from_current_list(todo_uid)
        todo_list = self._get_todo_list_by_id(list_id)
        todo_list.todos.insert(position, todo_uid)

    def move_todo_list(self, list_id, position):
        """Moves the given todo list to the new position

        arguments:
        list_id -- The ID of the todo-list
        position -- New position
        """
        todo_list = self._pop_todo_list(list_id)
        self._add_todo_list(todo_list, position)

    def list(self):
        """Returns a list of all todo-lists with its assigned todos.
        """
        return self._todo_lists

    def list_serialized(self, context=None):
        """Returns a list of all todo-lists in a serialized version.
        """
        return [todolist.serialize(context) for todolist in self.list()]

    def _insert_todo_list_in_storage(self, todo_list, position=0):
        self._storage[self.TODO_LISTS_KEY].insert(position, todo_list)
        return todo_list

    def _add_todo_list(self, todo_list, position=0):
        self._storage[self.TODO_LISTS_KEY].insert(position, todo_list)
        return todo_list

    def _pop_todo_list(self, list_id):
        todo_list = self._get_todo_list_by_id(list_id)
        filtered_todo_lists = filter(
            lambda todo_list: todo_list.id != list_id,
            self._storage[self.TODO_LISTS_KEY])

        self._storage[self.TODO_LISTS_KEY] = PersistentList(filtered_todo_lists)
        return todo_list

    def _get_todo_list_by_id(self, list_id):
        todo_list = self._todo_lists_by_id.get(list_id)
        if not todo_list:
            raise ToDoListStorageError(
                'List {} does not exist. Existing lists are: {}'.format(
                    list_id, self._todo_lists_by_id.keys()))

        return todo_list

    def _get_todo_list_by_todo_uid(self, todo_uid):
        todo_list = self._todos_by_uid.get(todo_uid)
        if not todo_list:
            raise ToDoListStorageError(
                'The todo with the id {} does not belong to any todo-list.'.format(
                    todo_uid))

        return todo_list

    @property
    def _todo_lists_by_id(self):
        return {
            todo_list.id: todo_list
            for todo_list in self._todo_lists
            }

    @property
    def _todos_by_uid(self):
        todos_by_uid = {}

        for todo_list in self._todo_lists:
            todos_by_uid.update({
                todo_uid: todo_list
                for todo_uid in todo_list.todos
            })

        return todos_by_uid

    @property
    def _todo_lists(self):
        return self._storage[self.TODO_LISTS_KEY]

    def _initialize_storage(self):
        ann = IAnnotations(self.context)
        if self.ANNOTATIONS_KEY not in ann:
            ann[self.ANNOTATIONS_KEY] = PersistentMapping({
                self.TODO_LISTS_KEY: PersistentList()
                })

        self._storage = ann[self.ANNOTATIONS_KEY]
