from ftw.dictstorage.interfaces import ISQLAlchemy
from zope.interface import implements


class DictStorageConfigurationContext(object):
    """Fake Object which provide the ISQLAlchemy Interface,
    so it's possible to get the ftw.dictstorage sqlstorage.
    """

    implements(ISQLAlchemy)
