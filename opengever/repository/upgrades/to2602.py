from ftw.upgrade import UpgradeStep


class RestrictPrefixManager(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.repository.upgrades:2602')
