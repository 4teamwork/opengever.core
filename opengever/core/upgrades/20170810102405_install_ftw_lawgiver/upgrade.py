from ftw.upgrade import UpgradeStep


class InstallFtwLawgiver(UpgradeStep):
    """Install ftw.lawgiver."""

    def __call__(self):
        self.setup_install_profile('profile-ftw.lawgiver:default')
