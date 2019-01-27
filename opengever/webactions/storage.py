from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from datetime import datetime
from opengever.webactions.exceptions import ActionAlreadyExists
from opengever.webactions.interfaces import IWebActionsStorage
from opengever.webactions.schema import IPersistedWebActionSchema
from opengever.webactions.schema import IWebActionSchema
from opengever.webactions.validation import validate_schema
from persistent.mapping import PersistentMapping
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


def get_storage():
    """Convencience function to easily get the IWebActionsStorage storage.
    """
    return getMultiAdapter((getSite(), getRequest()), IWebActionsStorage)


@implementer(IWebActionsStorage)
@adapter(IPloneSiteRoot, IBrowserRequest)
class WebActionsStorage(object):
    """Default IWebActionsStorage implementation.

    Stores webactions in annotations on the Plone site. See interface for
    detailed documentation.
    """

    ANNOTATIONS_KEY = 'opengever.webactions.storage'

    STORAGE_ACTIONS_KEY = 'actions'
    STORAGE_INDEXES_KEY = 'indexes'
    STORAGE_NEXT_ID_KEY = 'next_id'

    IDX_UNIQUE_NAME = 'unique_name_to_action_id'

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self._storage = None
        self._actions = None
        self._indexes = None
        self.initialize_storage()

    def initialize_storage(self):
        ann = IAnnotations(self.context)
        if self.ANNOTATIONS_KEY not in ann:
            ann[self.ANNOTATIONS_KEY] = OOBTree()

        self._storage = ann[self.ANNOTATIONS_KEY]

        # Actual list of actions
        if self.STORAGE_ACTIONS_KEY not in self._storage:
            self._storage[self.STORAGE_ACTIONS_KEY] = IOBTree()
        self._actions = self._storage[self.STORAGE_ACTIONS_KEY]

        # Indexes needed for fast lookups
        if self.STORAGE_INDEXES_KEY not in self._storage:
            self._storage[self.STORAGE_INDEXES_KEY] = OOBTree()
        self._indexes = self._storage[self.STORAGE_INDEXES_KEY]

        # Index: unique_name -> action_id
        if self.IDX_UNIQUE_NAME not in self._indexes:
            self._indexes[self.IDX_UNIQUE_NAME] = OIBTree()

        # Counter for the next 'action_id'
        if self.STORAGE_NEXT_ID_KEY not in self._storage:
            self._storage[self.STORAGE_NEXT_ID_KEY] = 0

    def issue_new_action_id(self):
        new_id = self._storage[self.STORAGE_NEXT_ID_KEY]
        self._storage[self.STORAGE_NEXT_ID_KEY] += 1
        return new_id

    def add(self, action_data):
        validate_schema(action_data, IWebActionSchema)

        self._enforce_unique_name_uniqueness(action_data)

        action_id = self.issue_new_action_id()

        new_action = PersistentMapping(action_data)
        self._actions[action_id] = new_action

        userid = api.user.get_current().getId()
        now = datetime.now()

        # The `action_id` is stored redundantly here in the actual
        # PersistentDict (as well as being used as the key in the IOBTree)
        #
        # This is so that the storage contents reflect (as closely as possible)
        # what's being returned by get() / list(), and can easily be validated
        # against a schema that consists of the user controlled fields plus
        # the server generated metadata.
        new_action['action_id'] = action_id
        new_action['created'] = now
        new_action['modified'] = now
        new_action['owner'] = userid if userid else 'Anonymous'

        self.index_action(new_action)
        return action_id

    def get(self, action_id):
        return self._actions[action_id]

    def list(self):
        if not self._actions:
            return []
        return self._actions.values()

    def update(self, action_id, action_data):
        action = self.get(action_id)

        self._enforce_unique_name_uniqueness(action_data)

        # Validate schema of the final resulting action on a copy
        action_copy = action.copy()
        action_copy.update(action_data)
        validate_schema(action_copy, IPersistedWebActionSchema)

        # If validation succeeded, update the actual PersistentDict
        self.unindex_action(action)

        action.update(action_data)
        action['modified'] = datetime.now()

        self.index_action(action)

    def delete(self, action_id):
        action = self.get(action_id)
        self.unindex_action(action)
        del self._actions[action_id]

    def index_action(self, action):
        action_id = action['action_id']

        # unique_name -> action_id
        if 'unique_name' in action:
            unique_name = action['unique_name']
            self._indexes[self.IDX_UNIQUE_NAME][unique_name] = action_id

    def unindex_action(self, action):
        # unique_name -> action_id
        if 'unique_name' in action:
            unique_name = action['unique_name']
            del self._indexes[self.IDX_UNIQUE_NAME][unique_name]

    def _enforce_unique_name_uniqueness(self, action_data):
        if 'unique_name' in action_data:
            unique_name = action_data['unique_name']
            if unique_name in self._indexes[self.IDX_UNIQUE_NAME]:
                raise ActionAlreadyExists(
                    'An action with the unique_name %r already '
                    'exists' % action_data['unique_name'])
