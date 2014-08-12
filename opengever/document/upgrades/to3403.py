from ftw.upgrade import UpgradeStep


class AddPublicTrialIndexAndMetadata(UpgradeStep):
    """Adds public_trial index and metadata"""

    def __call__(self):
        # add metadata field
        self.setup_install_profile(
            'profile-opengever.document.upgrades:3403')

        # add index
        if not self.catalog_has_index('public_trial'):
            self.catalog_add_index('public_trial', 'FieldIndex')

        # Indexes and metadata for these objects will be rebuilt in
        # upgrade step opengever.policy.base.upgrades:3400
