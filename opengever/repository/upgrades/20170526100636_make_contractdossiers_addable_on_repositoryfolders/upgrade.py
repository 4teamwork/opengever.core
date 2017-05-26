from ftw.upgrade import UpgradeStep


class MakeContractdossiersAddableOnRepositoryfolders(UpgradeStep):
    """Make contractdossiers addable on repositoryfolders.
    """

    def __call__(self):
        self.install_upgrade_profile()
