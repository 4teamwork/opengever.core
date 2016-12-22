from opengever.base.monkey.patching import MonkeyPatch


class PatchZCatalog(MonkeyPatch):

    def __call__(self):
        def sortResults(self, rs, sort_index, reverse=0, limit=None, merge=1,
                        actual_result_count=None, b_start=0, b_size=None):

            # The catalog does only use "documentToKeyMap" of the index
            # when limit is not None.
            # Since we use "documentToKeyMap" in order to use a different
            # value for sorting than the stored one (e.g. user fullname
            # instead of userid), we force the catalog to respect
            # "documentToKeyMap" by setting the limit to the amount of
            # entries in the catalog.

            if limit is None:
                limit = self._length()

            return original_sortResults(
                self,
                rs=rs,
                sort_index=sort_index,
                reverse=reverse,
                limit=limit,
                merge=merge,
                actual_result_count=actual_result_count,
                b_start=b_start,
                b_size=b_size)

        from Products.ZCatalog.Catalog import Catalog
        original_sortResults = Catalog.sortResults
        self.patch_refs(Catalog, 'sortResults', sortResults)
