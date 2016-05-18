from ftw.upgrade import UpgradeStep


class InstallBumblebeeProfile(UpgradeStep):
    """Install the opengever.bumblebee profile.
    """

    def __call__(self):
        self.install_upgrade_profile()
