from opengever.base.monkey.patching import MonkeyPatch


class PatchCatalogToFilterTrashedDocs(MonkeyPatch):
    """Patch catalog search results to filter trashed objects.

    This will omit trashed objects from search results by default, unless
    we explicitely ask for them using unrestrictedSearchResults().
    """

    def __call__(self):
        from Products.CMFPlone.CatalogTool import CatalogTool
        original_search_results = CatalogTool.searchResults

        def filtered_results(self, REQUEST=None, **kw):
            kw = kw.copy()

            # If no explicit query for 'trashed' present, filter out trashed
            # documents by default. REQUEST may be old-style ZCatalog query.
            if not ('trashed' in kw.keys() or
                    (REQUEST and 'trashed' in REQUEST)):
                kw['trashed'] = [False, None]

            return original_search_results(self, REQUEST, **kw)

        self.patch_refs(CatalogTool, 'searchResults', filtered_results)
        self.patch_refs(CatalogTool, '__call__', filtered_results)
