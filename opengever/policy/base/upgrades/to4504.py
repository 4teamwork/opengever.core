from ftw.upgrade import UpgradeStep
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile
from Products.ZCTextIndex.interfaces import IZCTextIndex


class ExecuteDelayedPloneUpgrade(UpgradeStep):
    """Redefine a patched plone upgrade step that is expensive.

    This upgrade step reindexes all ZCTextIndex fields. This step may take
    very long for customers with a lot of data. Thus we disable the default
    plone upgrade an redefine here to allow separate execution of this step.

    The plone upgrade step is monkey-patched in opengever.base.monkeypatch.
    """

    def __call__(self):
        self.load_migration_profile()
        self.reindex_zctext_indices()

    def load_migration_profile(self):
        loadMigrationProfile(self.portal_setup,
                             'profile-plone.app.upgrade.v43:to43rc1')

    def reindex_zctext_indices(self):
        """Rewrite of plone.app.upgrade.v43.alphas.upgradeToI18NCaseNormalizer
        to use ftw.upgrade progress logging.
        """

        catalog = api.portal.get_tool('portal_catalog')
        for index in catalog.Indexes.objectValues():
            if IZCTextIndex.providedBy(index):
                index_id = index.getId()
                # Clear index first to make sure lexicon gets updated properly
                catalog.manage_clearIndex([index_id])
                self.catalog_rebuild_index(index_id)
