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

        Raises a KeyError if the action_id doesn't exist.
        """

    def list(owner=None):
        """List all actions in the storage.

        If `owner` is given, only lists actions belonging to that user.
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


class IWebActionsProvider(Interface):
    """Multiadapter of context and request used to get all available
    webactions for a given user on a given context.
    """

    def get_webactions(self, display=None):
        """Returns a dictionary of all available webactions per display location
        ('display' location as key and list of webactions for that location as
        values). If display is passed, only webactions for that display type are
        returned.
        """


class IWebActionsRenderer(Interface):
    """Named Multiadapter of context and request used to render the webactions.
    The name of the multiadapter corresponds to the display location.
    """

    def __call__(self):
        """Returns the webactions as a list of markup used for the rendering at a given
        location.
        """
