from zope.interface import Interface


class IWebActionsStorage(Interface):
    """A IWebActionsStorage is responsible for persistently storing webactions.

    The default implementation stores them in annotations on the Plone site.

    The storage will also validate incoming data against the IWebActionSchema,
    and enforce invariants. These invariants may span a whole action, or even
    the entire storage (unique_name must be unique).

    In addition to storing the webactions' main data, the storage also keeps
    indexes required for common lookups that need to be fast.
    """

    def initialize_storage():
        """If not present already, initialize internal storage data structures.

        This method must be idempotent, so that if it's called more than once,
        it doesn't empty existing storage contents.
        """

    def issue_new_action_id():
        """Generate a new action_id that doesn't conflict with an existing one.
        """

    def add(action_data):
        """Add a new action to the storage, based on a dict with action data.
        """

    def get(action_id):
        """Retrieve an action by its action_id.
        """

    def list():
        """List all actions in the storage.
        """

    def update(action_id, action_data):
        """Update the action identified by action_id.
        """

    def delete(action_id):
        """Delete the action identified by action_id.
        """

    def index_action(action):
        """Index the given persistent action.
        """

    def unindex_action(action):
        """Unindex the given peristent action.
        """
