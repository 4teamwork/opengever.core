from ftw.upgrade import UpgradeStep


class RemoveResponsibleJs(UpgradeStep):
    """Remove responsible.js.
    """

    def __call__(self):
        self.install_upgrade_profile()
