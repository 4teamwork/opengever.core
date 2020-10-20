from ftw.dictstorage.sql import DictStorage as SQLDictStorage
from opengever.readonly import is_in_readonly_mode


class ReadOnlyCapableSQLDictStorage(SQLDictStorage):
    """DictStorage that reads from, but doesn't write to SQL when
    instance is in readonly mode.
    """

    def __init__(self, context, session):
        self.context = context
        self.session = session

        self.readonly = is_in_readonly_mode()

    def __setitem__(self, key, value):
        if self.readonly:
            return

        return super(ReadOnlyCapableSQLDictStorage, self).__setitem__(key, value)

    def __delitem__(self, key):
        if self.readonly:
            return

        return super(ReadOnlyCapableSQLDictStorage, self).__delitem__(key)
