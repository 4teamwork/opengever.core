from ftw.upgrade import UpgradeStep


class AddRespectMaxDepthRegistryEntryForDossiertemplates(UpgradeStep):
    """Add respect_max_depth registry entry for dossiertemplates.
    """

    def __call__(self):
        self.install_upgrade_profile()
