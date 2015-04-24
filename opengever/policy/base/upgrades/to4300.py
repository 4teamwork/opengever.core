from ftw.upgrade import UpgradeStep


class InstallFtwFooter(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-ftw.footer:default')
