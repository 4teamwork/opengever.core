from copy import copy


class TempMonkeyPatch(object):
    """Context manager to temporarily monkey patch an object's attribute.

    Only meant to be used in tests!

    This context manager will back up the attribute's original value, patch
    it to a new value, and upon leaving the context, restore the original
    value.
    """

    def __init__(self, target_obj, target_attr, new_value):
        self.target_obj = target_obj
        self.target_attr = target_attr
        self.new_value = new_value

    def backup(self):
        self.original_value = copy(getattr(self.target_obj, self.target_attr))

    def patch(self):
        setattr(self.target_obj, self.target_attr, self.new_value)

    def restore(self):
        setattr(self.target_obj, self.target_attr, self.original_value)

    def __enter__(self):
        """Back up the original value and batch the target object's attribute.
        """
        self.backup()
        self.patch()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Restore the original value to the target object's attribute.
        """
        self.restore()


def patch_collective_indexing():
    """During tests, patch collective.indexing's IndexQueue so that it
    doesn't defer (re)indexing to the end of the transaction, but instead
    executes these operations immediately (by always processing the queue).

    This allows us to still have c.indexing active during tests, to make use
    of it's pluggable IndexQueueProcessor mechanism (used to integrate Solr),
    but not have the negative side effects from deferred indexing.
    """
    from collective.indexing.queue import IndexQueue
    from collective.indexing.queue import processQueue

    orig_index = IndexQueue.index

    def index(self, obj, attributes=None):
        result = orig_index(self, obj, attributes=attributes)
        processQueue()
        return result

    orig_reindex = IndexQueue.reindex

    def reindex(self, obj, attributes=None):
        result = orig_reindex(self, obj, attributes=attributes)
        processQueue()
        return result

    orig_unindex = IndexQueue.unindex

    def unindex(self, obj):
        result = orig_unindex(self, obj)
        processQueue()
        return result

    IndexQueue.index = index
    IndexQueue.reindex = reindex
    IndexQueue.unindex = unindex


def patch_demostorage_to_support_readonly_mode():
    """During tests, patch DemoStorage to support ReadOnly mode.

    This set of patches is "always-on", during all of the tests, irrespective
    of whether the context manager that actually *enables* read-only mode is
    being used or not.

    They only provide the support infrastructure to be able to turn read-only
    mode on in tests. This involves two aspects:

    - Make DemoStorage.isReadOnly() answer correctly whether RO is enabled.
    - Have DemoStorage raise POSException.ReadOnlyError in the same places
      that ZEO.ClientStorage would if writes are attempted in RO mode.
    """
    from ZODB import POSException
    from ZODB.DemoStorage import DemoStorage
    import ZODB.utils

    # This method is the public API of a storage to determine whether it's in
    # read-only mode, and will be called by Connection.isReadOnly().
    # DemoStorage doesn't usually implement this (directly). We patch it
    # into DemoStorage's class dict, but that is not quite enough yet.

    def isReadOnly(self):
        return getattr(self, '_is_read_only', False)

    DemoStorage.isReadOnly = isReadOnly

    # DemoStorage actually copies over some methods from MappingStorage into
    # its own *instance* dict during DS.__init__. Among them 'isReadOnly'
    # (a dummy implementation that just returns False).
    #
    # Therefore that dummy method in the instance dict will be found *first*
    # by Python's method lookup, shadowing our method in the class dict and
    # making it ineffective.
    #
    # (See _copy_methods_from_changes() in ZODB.DemoStorage)
    #
    # We therefore patch that method to delete the 'isReadOnly' method from
    # the instance dict again, immediately after it has been copied.

    orig_copy_methods_from_changes = DemoStorage._copy_methods_from_changes

    def wrapped_copy_methods_from_changes(self, changes):
        orig_copy_methods_from_changes(self, changes)
        del self.isReadOnly

    DemoStorage._copy_methods_from_changes = wrapped_copy_methods_from_changes

    # With these changes DemoStorage is ready to answer truthfully in its
    # isReadOnly() method. What follows now is actually suppressing writes
    # by raising POSException.ReadOnlyError in the right places.
    #
    # This is done in a way that emulates the code in ZEO.ClientStorage as
    # closely as possible (including the indirection through _check_trans()),
    # in order for the two implementations to be easier to compare.

    # === IStorage.tpc_begin

    orig_tpc_begin = DemoStorage.tpc_begin

    @ZODB.utils.locked
    def wrapped_tpc_begin(self, transaction, *a, **k):
        if getattr(self, '_is_read_only', False):
            raise POSException.ReadOnlyError()
        return orig_tpc_begin(self, transaction, *a, **k)

    DemoStorage.tpc_begin = wrapped_tpc_begin

    # === IStorage.new_oid

    orig_new_oid = DemoStorage.new_oid

    @ZODB.utils.locked
    def wrapped_new_oid(self):
        if getattr(self, '_is_read_only', False):
            raise POSException.ReadOnlyError()
        return orig_new_oid(self)

    DemoStorage.new_oid = wrapped_new_oid

    # === ClientStorage._check_trans

    def _check_trans(self, trans):
        """Emulates the readonly part of ClientStorage._check_trans"""
        if getattr(self, '_is_read_only', False):
            raise POSException.ReadOnlyError()

    DemoStorage._check_trans = _check_trans

    # === IStorage.store

    orig_store = DemoStorage.store

    def wrapped_store(self, oid, serial, data, version, txn):
        self._check_trans(txn)
        return orig_store(self, oid, serial, data, version, txn)

    DemoStorage.store = wrapped_store

    # === ReadVerifyingStorage.checkCurrentSerialInTransaction

    orig_checkCurrentSerialInTransaction = DemoStorage.checkCurrentSerialInTransaction

    def wrapped_checkCurrentSerialInTransaction(self, oid, serial, txn):
        self._check_trans(txn)
        return orig_checkCurrentSerialInTransaction(self, oid, serial, txn)

    DemoStorage.checkCurrentSerialInTransaction = wrapped_checkCurrentSerialInTransaction

    # DemoStorage doesn't support 'deleteObject', 'undo' or 'restore',
    # therefore these methods implemented by ZEO.ClientStorage don't exist
    # and don't need to be patched.
