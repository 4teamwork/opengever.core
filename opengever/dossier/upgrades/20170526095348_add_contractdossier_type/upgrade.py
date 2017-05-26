from ftw.upgrade import UpgradeStep


class AddContractdossierType(UpgradeStep):
    """Add contractdossier type.
    """

    def __call__(self):
        self.install_upgrade_profile()
