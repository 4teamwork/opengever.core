from opengever.base.monkey.patching import MonkeyPatch


class PatchUUIDIndex(MonkeyPatch):
    """Enable support for not queries."""

    def __call__(self):
        from Products.PluginIndexes.UUIDIndex.UUIDIndex import UUIDIndex
        self.patch_value(UUIDIndex, 'query_options', ["query", "range", "not"])
