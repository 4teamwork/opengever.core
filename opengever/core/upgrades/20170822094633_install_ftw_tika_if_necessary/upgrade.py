from ftw.upgrade import UpgradeStep


class InstallFtwTikaIfNecessary(UpgradeStep):
    """Install ftw.tika if necessary.
    """

    def __call__(self):
        self.ensure_profile_installed('profile-ftw.tika:default')
