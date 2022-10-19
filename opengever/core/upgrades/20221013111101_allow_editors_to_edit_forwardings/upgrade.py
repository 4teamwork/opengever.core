from ftw.upgrade import UpgradeStep


class AllowEditorsToEditForwardings(UpgradeStep):
    """Allow editors to edit forwardings.
    """

    def __call__(self):
        self.install_upgrade_profile()
