from ftw.upgrade import UpgradeStep


class AddUseChangedForEndDateRegistryField(UpgradeStep):
    """Add use_changed_for_end_date registry field.
    """

    def __call__(self):
        self.install_upgrade_profile()
