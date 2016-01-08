from ftw.upgrade import UpgradeStep


class RemoveModifiedSecondsIndex(UpgradeStep):

    def __call__(self):
        index_name = 'modified_seconds'
        if self.catalog_has_index(index_name):
            self.catalog_remove_index(index_name)
