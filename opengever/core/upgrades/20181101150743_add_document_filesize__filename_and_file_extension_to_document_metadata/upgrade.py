from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument


class AddDocumentFilesize_filenameAndFileExtensionToDocumentMetadata(UpgradeStep):
    """Add document filesize, filename and file extension to document metadata.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        self.catalog_add_index('filesize', 'FieldIndex')
        self.catalog_add_index('file_extension', 'FieldIndex')

        query = {
            'object_provides': IBaseDocument.__identifier__,
            }

        for basedocument in self.objects(query, 'Index filesize, filename and file extension of IBaseDocument objects.'):
            basedocument.reindexObject(idxs=['filesize', 'file_extension'])
