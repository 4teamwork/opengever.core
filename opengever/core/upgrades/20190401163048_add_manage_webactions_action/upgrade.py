from ftw.upgrade import UpgradeStep


class AddManageWebactionsAction(UpgradeStep):
    """Add manage webactions action.
    """

    def __call__(self):
        self.install_upgrade_profile()
