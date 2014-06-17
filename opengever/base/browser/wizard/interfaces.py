# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument


from zope.interface import Interface


class IWizardDataStorage(Interface):
    """Storage for storing wizard-data in annotations on the plone site. The
    storage can also be transported to another client.

    The storage is personal and cleaned up on the first use after
    `STORAGE_TIMEOUT` seconds.
    """

    def get_data(key):
        """Returns the data set (dict) stored under `key` in the storage. If
        there is no data set, a new one is crated.

        Arguments:
        key -- String key to identify the data set.
        """

    def update(key, data):
        """Updates the data set stored under `key` with `data` (dict).

        Arguments:
        key -- String key to identify the data set.
        data -- Dict of data to be stored in the data set.
        """

    def get(key, datakey, default=None):
        """Returns the value stored under `datakey` in the data set identified
        by `key`.

        Arguments:
        key -- String key to identify the data set.
        datakey -- String key of the value within the data set.
        default -- Default to be returned when the value is not found.
        """

    def set(key, datakey, value):
        """Stores a value under `datakey` in the data set identified by `key`.

        Arguments:
        key -- String key to identify the data set.
        datakey -- String key of the value within the data set.
        value -- The value to be set.
        """

    def push_to_remote_client(key, admin_unit_id):
        """Push the data set stored under `key` to the admin unit
        `admin_unit_id`.

        Arguments:
        key -- String key to identify the data set.
        admin_unit_id -- Target admin unit id.
        """
