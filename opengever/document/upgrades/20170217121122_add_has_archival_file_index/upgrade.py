from ftw.upgrade import UpgradeStep


class AddHasArchivalFileIndex(UpgradeStep):
    """Add has_archival_file index.
    """

    def __call__(self):
        index_name = 'has_archival_file'
        self.catalog_add_index(index_name, 'BooleanIndex')
        self.catalog_rebuild_index(index_name)
