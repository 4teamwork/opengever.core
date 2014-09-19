from ftw.upgrade import UpgradeStep


class AddModifiedSecondsIndex(UpgradeStep):

    def __call__(self):
        index_name = 'modified_seconds'
        if self.catalog_has_index(index_name):
            return

        self.catalog_add_index(index_name, 'FieldIndex')
        self.catalog_reindex_objects({},
                                     idxs=[index_name],
                                     savepoints=500)
