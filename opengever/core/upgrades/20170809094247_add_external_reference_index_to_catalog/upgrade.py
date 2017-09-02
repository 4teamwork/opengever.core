from ftw.upgrade import UpgradeStep


class AddExternalReferenceIndexToCatalog(UpgradeStep):
    """Add indexes to catalog.
    """

    def __call__(self):
        self.catalog_add_index('external_reference', 'FieldIndex')
