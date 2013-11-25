from ftw.upgrade import UpgradeStep


class RegisterSkinsDirectory(UpgradeStep):
    """Register opengever.advancedsearch skins directory"""

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.advancedsearch.upgrades:2202')
