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
