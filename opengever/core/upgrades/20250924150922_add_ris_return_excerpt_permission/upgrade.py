from ftw.upgrade import UpgradeStep


class AddRisReturnExcerptPermission(UpgradeStep):
    """Add ris return excerpt permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
