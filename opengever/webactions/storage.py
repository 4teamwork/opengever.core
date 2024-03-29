from BTrees.IIBTree import IITreeSet
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from datetime import datetime
from opengever.api.validation import validate_no_unknown_fields
from opengever.api.validation import validate_schema
from opengever.webactions.exceptions import ActionAlreadyExists
from opengever.webactions.exceptions import ForbiddenTargetUrlParam
from opengever.webactions.exceptions import UnsupportedTargetUrlPlaceholder
from opengever.webactions.interfaces import IWebActionsStorage
from opengever.webactions.schema import IPersistedWebActionSchema
from opengever.webactions.schema import IWebActionSchema
from persistent.mapping import PersistentMapping
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from urlparse import parse_qs
from urlparse import urlparse
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


DEFAULT_QUERY_PARAMS = [
    'context',
    'orgunit',
]

ALLOWED_QUERY_PLACEHOLDERS = [
    '{intid}',
    '{path}',
    '{uid}',
]


def get_storage():
    """Convencience function to easily get the IWebActionsStorage storage.
    """
    return getMultiAdapter((getSite(), getRequest()), IWebActionsStorage)


def is_placeholder(placeholder):
    return placeholder.startswith('{') and placeholder.endswith('}')


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
    STORAGE_CONTEXT_INTIDS_KEY = 'context_intids'

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

        # Actual dict of context uids per actionid
        if self.STORAGE_CONTEXT_INTIDS_KEY not in self._storage:
            self._storage[self.STORAGE_CONTEXT_INTIDS_KEY] = PersistentMapping()
        self._context_intids = self._storage[self.STORAGE_CONTEXT_INTIDS_KEY]

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
        self._enforce_valid_query_params(action_data)

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

        # Some userids are unicode others are strings, so we need to make sure
        # to cast them to the correct type
        new_action['owner'] = safe_unicode(userid) if userid else u'Anonymous'

        # To be sure to only store valid webactions, we also validate
        # with the automatically added data
        validate_schema(new_action, IPersistedWebActionSchema)

        self.index_action(new_action)
        return action_id

    def add_context_intid(self, action_id, intid):
        if not self._actions.get(action_id):
            raise NotFound('Action with action_id {} does not exist'.format(action_id))
        if self._actions[action_id]['scope'] != 'context':
            raise Forbidden('Actions can only be activated if they have scope context.')
        if not self._context_intids.get(action_id):
            self._context_intids[action_id] = IITreeSet()
        self._context_intids[action_id].insert(intid)

    def remove_context_intid(self, action_id, intid):
        self._context_intids[action_id].remove(intid)

    def get_context_intids(self, action_id):
        return set(self._context_intids.get(action_id, []))

    def list_context_intids(self):
        return [{'action_id': k, 'context_intids': list(v)}
                for k, v in self._context_intids.items()]

    def get(self, action_id):
        return dict(self._actions[action_id])

    def list(self, owner=None):
        if owner is not None:
            return [dict(a) for a in self._actions.values() if a['owner'] == owner]

        return [dict(a) for a in self._actions.values()]

    def update(self, action_id, action_data):
        persisted_action = self._actions[action_id]

        # Make sure we only allow updating of the user-controlled fields from
        # the IWebActionSchema, but reject server-controlled ones or other
        # surprise data.
        validate_no_unknown_fields(action_data, IWebActionSchema)

        self._enforce_unique_name_uniqueness(action_data)
        self._enforce_valid_query_params(action_data)

        # Validate schema of the final resulting action on a copy
        action_copy = persisted_action.copy()
        action_copy.update(action_data)
        validate_schema(action_copy, IPersistedWebActionSchema)

        # If validation succeeded, update the actual PersistentDict
        self.unindex_action(persisted_action)

        persisted_action.update(action_data)
        persisted_action['modified'] = datetime.now()

        self.index_action(persisted_action)

    def delete(self, action_id):
        action = self._actions[action_id]
        self.unindex_action(action)
        del self._actions[action_id]
        if self._context_intids.get(action_id):
            del self._context_intids[action_id]

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

    def _enforce_valid_query_params(self, action_data):
        target_url = action_data.get('target_url')
        if not target_url:
            return
        query = parse_qs(urlparse(target_url).query)
        if not query:
            return
        for param, value in query.items():
            if param in DEFAULT_QUERY_PARAMS:
                raise ForbiddenTargetUrlParam(
                    'The query parameter "{}" is not allowed because it will be '
                    'provided automatically.'.format(param)
                )
            for placeholder in value:
                if is_placeholder(placeholder) and placeholder not in ALLOWED_QUERY_PLACEHOLDERS:
                    raise UnsupportedTargetUrlPlaceholder(
                        'The placeholder "{}" of the query parameter "{}" is not '
                        'supported.'.format(placeholder, param)
                    )
