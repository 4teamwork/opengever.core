from ftw.upgrade import UpgradeStep
from plone.dexterity.interfaces import IDexterityContainer


class AddHasSameTypeChildrenMetadataColumn(UpgradeStep):
    """Add has same type children metadata column.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        query = {
            'object_provides': IDexterityContainer.__identifier__,
            }
        # To avoid reindexing the whole objects, we pick any index that exists
        # for all objects and is fast to compute
        self.catalog_reindex_objects(query, idxs=['UID', 'has_sametype_children'])
