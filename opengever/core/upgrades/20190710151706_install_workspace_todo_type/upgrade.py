from ftw.upgrade import UpgradeStep


class InstallWorkspaceTodoType(UpgradeStep):
    """Install workspace todo type.
    """

    def __call__(self):
        self.install_upgrade_profile()
