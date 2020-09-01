from ftw.upgrade import UpgradeStep


class AddShareContentAction(UpgradeStep):
    """Add share_content action.
    """

    def __call__(self):
        self.install_upgrade_profile()
