from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from datetime import datetime
from opengever.webactions.interfaces import IWebActionsStorage
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
    STORAGE_NEXT_ID_KEY = 'next_id'

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self._storage = None
        self._actions = None
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

        # Counter for the next 'action_id'
        if self.STORAGE_NEXT_ID_KEY not in self._storage:
            self._storage[self.STORAGE_NEXT_ID_KEY] = 0

    def issue_new_action_id(self):
        new_id = self._storage[self.STORAGE_NEXT_ID_KEY]
        self._storage[self.STORAGE_NEXT_ID_KEY] += 1
        return new_id

    def add(self, action_data):
        # TODO: Schema Validation
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

        return action_id

    def get(self, action_id):
        return self._actions[action_id]

    def list(self):
        if not self._actions:
            return []
        return self._actions.values()

    def update(self, action_id, action_data):
        # TODO: Schema Validation
        action = self.get(action_id)
        action.update(action_data)
        action['modified'] = datetime.now()

    def delete(self, action_id):
        del self._actions[action_id]
