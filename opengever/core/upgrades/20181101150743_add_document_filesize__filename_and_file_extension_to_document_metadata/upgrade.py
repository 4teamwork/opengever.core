from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument


class AddDocumentFilesize_filenameAndFileExtensionToDocumentMetadata(UpgradeStep):
    """Add document filesize, filename and file extension to document metadata.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        if not self.catalog_has_index('filesize'):
            self.catalog_add_index('filesize', 'FieldIndex')

        if not self.catalog_has_index('file_extension'):
            self.catalog_add_index('file_extension', 'FieldIndex')

        query = {
            'object_provides': IBaseDocument.__identifier__,
            }

        for basedocument in self.objects(query, 'Index filesize, filename and file extension of IBaseDocument objects.'):

            # There is no index called filename, but we need to add it to the
            # idxs list, to make sure that solr's filename index is indexed
            # as well.
            basedocument.reindexObject(
                idxs=['filesize', 'file_extension', 'filename'])
