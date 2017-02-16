from ftw.upgrade import UpgradeStep


class AllowAddRootContentOnlyForManager(UpgradeStep):
    """Allow add root content only for manager.
    """

    def __call__(self):
        self.install_upgrade_profile()

