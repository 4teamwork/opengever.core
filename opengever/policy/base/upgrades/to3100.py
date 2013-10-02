from ftw.upgrade import UpgradeStep


class EnableZipexport(UpgradeStep):
    """ Install zipexport and mark dossiers as zipexport supported types. """

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.zipexport:default')
        self.setup_install_profile(
            'profile-opengever.policy.base.upgrades:3100')
