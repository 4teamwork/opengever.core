from ftw.upgrade import UpgradeStep


class UpdateVocabUsedForPublicTrialDefaultValueRegistryRecord(UpgradeStep):
    """Update vocab used for public_trial_default_value registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
