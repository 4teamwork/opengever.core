from ftw.upgrade import UpgradeStep


class InstallFtwFooter(UpgradeStep):

    def __call__(self):
        # ftw.footer was removed.
        # self.setup_install_profile('profile-ftw.footer:default')
        pass
