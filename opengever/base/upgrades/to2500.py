from ftw.upgrade import UpgradeStep


class RegisterBrowserLayer(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.base.upgrades:2500')
