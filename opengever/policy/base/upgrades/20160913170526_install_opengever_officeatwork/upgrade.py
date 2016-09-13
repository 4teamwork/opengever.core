from ftw.upgrade import UpgradeStep


class InstallOpengeverOfficeatwork(UpgradeStep):
    """install opengever.officeatwork.
    """

    def __call__(self):
        self.install_upgrade_profile()
