from ftw.upgrade import UpgradeStep


INDEX_NAME = 'is_subdossier'


class ReplaceIsSubdossierFieldIndexWithABooleanIndex(UpgradeStep):
    """Replace is_subdossier field index with a boolean index if
    necessary.
    """

    def __call__(self):
        index = self.portal.portal_catalog.Indexes.get(INDEX_NAME)
        if index.__class__.__name__ != 'BooleanIndex':
            self.catalog_remove_index(INDEX_NAME)
            self.catalog_add_index(INDEX_NAME, 'BooleanIndex')
            self.catalog_rebuild_index(INDEX_NAME)
