from ftw.dictstorage.interfaces import IDictStorage
from ftw.dictstorage.interfaces import ISQLAlchemy
from zope.interface import implements


class DictStorageConfigurationContext(object):
    """Fake Object which provide the ISQLAlchemy Interface,
    so it's possible to get the ftw.dictstorage sqlstorage.
    """

    implements(ISQLAlchemy)


def get(key):
    """Retrieve a value from the key-value store."""
    return IDictStorage(DictStorageConfigurationContext()).get(key)


def set(key, value):
    """Set a value in the key-value store."""
    return IDictStorage(DictStorageConfigurationContext()).set(key, value)
