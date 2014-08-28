from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument


class RebuildIndexesForDocumentishObjects(UpgradeStep):
    """Rebuild required indexes and metadata for all documentish objects.

    This is a merged / optimized upgrade step required after the changes in
    opengever.mail.upgrades:3401
    opengever.mail.upgrades:3402
    opengever.document.upgrades:3403
    """

    def __call__(self):
        idxs = [
            'document_date',
            'document_author',
            'delivery_date',
            'receipt_date',
            'object_provides',
            'privacy_layer',
            'public_trial',
        ]
        self.catalog_reindex_objects(
            {'object_provides': IBaseDocument.__identifier__},
            idxs=idxs)
