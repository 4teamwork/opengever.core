from ftw.upgrade import UpgradeStep


class OrderWebactionTitleButtonsViewlet(UpgradeStep):
    """Order webaction title buttons viewlet.
    """

    def __call__(self):
        self.install_upgrade_profile()
