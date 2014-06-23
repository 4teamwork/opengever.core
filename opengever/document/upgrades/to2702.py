from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument


class AddPublicTrialIndexAndMetadata(UpgradeStep):
    """Adds public_trial index and metadata"""

    def __call__(self):
        # add metadata field
        self.setup_install_profile(
            'profile-opengever.document.upgrades:2702')

        # add index
        if not self.catalog_has_index('public_trial'):
            self.catalog_add_index('public_trial', 'FieldIndex')

        self.catalog_reindex_objects(
            {'object_provides': IBaseDocument.__identifier__},
            idxs=['public_trial'])
