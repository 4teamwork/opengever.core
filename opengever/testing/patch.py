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
