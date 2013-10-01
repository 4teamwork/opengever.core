from ftw.upgrade import UpgradeStep


class EnableZipexport(UpgradeStep):
    """ Add zipexport marker to all supported types """

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.zipexport:default')
        self.setup_install_profile(
            'profile-opengever.policy.base.upgrades:3100')
