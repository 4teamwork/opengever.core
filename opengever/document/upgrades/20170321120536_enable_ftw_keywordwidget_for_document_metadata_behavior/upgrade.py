from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata


class EnableFtwKeywordwidgetForDocumentMetadataBehavior(UpgradeStep):
    """Enable ftw keywordwidget for document metadata behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.catalog_reindex_objects(
            {'object_provides': [IDocumentMetadata.__identifier__]},
            idxs=['Subject', ])
