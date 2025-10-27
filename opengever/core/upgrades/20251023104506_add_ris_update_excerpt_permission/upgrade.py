from ftw.upgrade import UpgradeStep


class AddRisUpdateExcerptPermission(UpgradeStep):
    """Add ris update excerpt permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
