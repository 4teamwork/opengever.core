from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument


class AddDocumentTypeIndex(UpgradeStep):
    """Add document_type index.
    """

    deferrable = True

    def __call__(self):
        if not self.catalog_has_index('document_type'):
            self.catalog_add_index('document_type', 'FieldIndex')

        query = {
            'object_provides': IBaseDocument.__identifier__,
            }

        self.catalog_reindex_objects(query, idxs=['document_type'])
