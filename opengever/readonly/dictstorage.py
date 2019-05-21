from ftw.dictstorage.sql import DictStorage
from zope.component.hooks import getSite


class ReadOnlySQLDictStorage(DictStorage):
    """DictStorage that reads from, but doesn't write to SQL when
    instance is in readonly mode.
    """

    def __init__(self, context, session):
        self.context = context
        self.session = session

        conn = getSite()._p_jar
        self.readonly = conn.isReadOnly()

    def __setitem__(self, key, value):
        if self.readonly:
            return
        return super(ReadOnlySQLDictStorage, self).__setitem__(key, value)

    def __delitem__(self, key):
        if self.readonly:
            return
        return super(ReadOnlySQLDictStorage, self).__delitem__(key)
