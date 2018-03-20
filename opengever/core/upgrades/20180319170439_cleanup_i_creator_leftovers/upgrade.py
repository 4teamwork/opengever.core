from ftw.upgrade import UpgradeStep
from plone import api


class CleanupICreatorLeftovers(UpgradeStep):
    """Cleanup i creator leftovers.
    """

    def __call__(self):
        self.reindex_object_provides()

    def reindex_object_provides(self):
        catalog = api.portal.get().portal_catalog
        query = {'object_provides': ['opengever.base.behaviors.creator.ICreatorAware']}
        message = "Remove references to ICreatorAware interface:"
        message += " reindexing object_provides"
        for obj in self.objects(query, message):
            catalog.reindexObject(
                obj, idxs=['object_provides'], update_metadata=False)
