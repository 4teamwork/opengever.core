from ftw.upgrade import UpgradeStep


class RemoveRelatedItemsIndex(UpgradeStep):
    """Removes the related_items index."""

    def __call__(self):
        index_name = 'related_items'
        if self.catalog_has_index(index_name):
            self.catalog_remove_index(index_name)
