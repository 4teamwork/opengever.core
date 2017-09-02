from ftw.upgrade import UpgradeStep


class RemoveUnusedProjectdossier(UpgradeStep):
    """Remove unused projectdossier.
    """

    def __call__(self):
        self.install_upgrade_profile()
