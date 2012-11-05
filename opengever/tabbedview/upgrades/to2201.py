from ftw.upgrade import UpgradeStep


class InstallFtwTooltip(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.tooltip:default')
