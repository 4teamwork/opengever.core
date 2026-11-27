from ftw.upgrade import UpgradeStep


class AddSharingGroupFilterAttribute(UpgradeStep):
    """Register the sharing group filter attribute setting."""

    def __call__(self):
        self.install_upgrade_profile()
