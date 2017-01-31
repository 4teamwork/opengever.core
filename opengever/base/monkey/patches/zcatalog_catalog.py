from opengever.base.monkey.patching import MonkeyPatch


class PatchZCatalog(MonkeyPatch):

    def __call__(self):

        def _getSortIndex(self, args):
            index = original_getSortIndex(self, args)
            if hasattr(index, 'get_sort_index'):
                return index.get_sort_index()
            else:
                return index

        from Products.ZCatalog.Catalog import Catalog
        original_getSortIndex = Catalog._getSortIndex
        self.patch_refs(Catalog, '_getSortIndex', _getSortIndex)
